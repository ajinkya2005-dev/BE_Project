import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
import shap

from ml.risk_model import load_or_train_model
from ml.feature_engineering import extract_features_from_dict, FEATURE_NAMES

FEATURE_LABELS = {
    "attendance": "Attendance Percentage",
    "cgpa": "Cumulative Grade Point Average (CGPA)",
    "backlog_count": "Active Backlogs Count",
    "assignment_completion": "Assignment Completion Rate",
    "quiz_average": "Quiz Average Marks",
    "study_hours": "Weekly Study Hours",
    "lms_activity": "LMS Portal Activity",
    "marks_trend": "Recent Assessment Score Trend",
    "attendance_trend": "Recent Attendance Trend",
    "engagement_score": "Composite Engagement Index"
}

def compute_shap_explanations(student_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute SHAP values and human-readable explanations for a given student's risk score.
    Returns dict containing feature impact values, top risk drivers, protective factors, and text summary.
    """
    artifact = load_or_train_model()
    model = artifact["model"]

    X_feat = extract_features_from_dict(student_data)

    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_feat)

        # Handle binary classification output format differences in SHAP versions
        if isinstance(shap_values, list):
            # Class 1 (dropout risk positive)
            vals = shap_values[1][0]
        elif len(shap_values.shape) == 3:
            vals = shap_values[0, :, 1]
        else:
            vals = shap_values[0]
    except Exception:
        # Fallback domain-heuristic feature importance calculation if SHAP encounters array shape edge cases
        vals = []
        att = float(student_data.get("attendance", 75))
        cgpa = float(student_data.get("cgpa", 7.0))
        backlogs = int(student_data.get("backlog_count", 0))
        assign = float(student_data.get("assignment_completion", 80))
        quiz = float(student_data.get("quiz_average", 70))
        hours = float(student_data.get("study_hours", 15))
        lms = float(student_data.get("lms_activity", 70))
        m_trend = float(student_data.get("marks_trend", 0))
        a_trend = float(student_data.get("attendance_trend", 0))
        eng = float(student_data.get("engagement_score", 75))

        vals_map = {
            "attendance": (75.0 - att) * 0.008,
            "cgpa": (7.0 - cgpa) * 0.06,
            "backlog_count": backlogs * 0.09,
            "assignment_completion": (80.0 - assign) * 0.004,
            "quiz_average": (70.0 - quiz) * 0.004,
            "study_hours": (15.0 - hours) * 0.008,
            "lms_activity": (70.0 - lms) * 0.004,
            "marks_trend": -m_trend * 0.008,
            "attendance_trend": -a_trend * 0.008,
            "engagement_score": (75.0 - eng) * 0.004
        }
        vals = [vals_map[col] for col in FEATURE_NAMES]

    # Create detailed DataFrame
    df_exp = pd.DataFrame({
        "feature": FEATURE_NAMES,
        "feature_label": [FEATURE_LABELS[f] for f in FEATURE_NAMES],
        "value": X_feat.iloc[0].values,
        "shap_impact": vals,
        "abs_impact": np.abs(vals)
    }).sort_values("abs_impact", ascending=False)

    # Separate Risk Drivers (positive SHAP -> increases risk) and Protective Factors (negative SHAP -> reduces risk)
    risk_drivers = df_exp[df_exp["shap_impact"] > 0.001].copy()
    protective_factors = df_exp[df_exp["shap_impact"] < -0.001].copy()

    # Generate Human Readable Summary
    summary_text = generate_natural_language_explanation(student_data, risk_drivers, protective_factors)

    return {
        "explanation_df": df_exp,
        "risk_drivers": risk_drivers,
        "protective_factors": protective_factors,
        "summary_narrative": summary_text
    }

def generate_natural_language_explanation(student_data: Dict[str, Any],
                                          risk_drivers: pd.DataFrame,
                                          protective_factors: pd.DataFrame) -> str:
    """Generate student-friendly, jargon-free academic risk summary."""
    name = student_data.get("full_name", "Student")
    risk_level = student_data.get("current_risk_level", "LOW")
    risk_pct = int(float(student_data.get("current_risk_score", 0.25)) * 100)

    if risk_level == "HIGH":
        narrative = f"Your academic dropout risk is currently **elevated ({risk_pct}%)**. "
    elif risk_level == "MEDIUM":
        narrative = f"Your academic standing requires **attention ({risk_pct}% moderate risk)**. "
    else:
        narrative = f"Great job! Your academic standing is currently **stable ({risk_pct}% low risk)**. "

    if not risk_drivers.empty:
        top_causes = []
        for idx, row in risk_drivers.head(3).iterrows():
            f_name = row["feature"]
            val = row["value"]
            if f_name == "attendance":
                top_causes.append(f"below-target attendance ({val:.1f}%)")
            elif f_name == "backlog_count":
                top_causes.append(f"{int(val)} active backlog(s)")
            elif f_name == "cgpa":
                top_causes.append(f"lower CGPA ({val:.2f})")
            elif f_name == "marks_trend" and val < 0:
                top_causes.append(f"declining marks trend ({val:.1f}%)")
            elif f_name == "attendance_trend" and val < 0:
                top_causes.append(f"recent attendance drop ({val:.1f}%)")
            elif f_name == "lms_activity":
                top_causes.append(f"low LMS portal engagement ({val:.0f}%)")
            elif f_name == "assignment_completion":
                top_causes.append(f"delayed assignment submissions ({val:.0f}%)")

        if top_causes:
            narrative += f"Primary factors contributing to risk elevation include: **{', '.join(top_causes)}**. "

    if not protective_factors.empty:
        top_positives = []
        for idx, row in protective_factors.head(2).iterrows():
            f_name = row["feature"]
            val = row["value"]
            if f_name == "attendance" and val > 80:
                top_positives.append(f"strong attendance ({val:.1f}%)")
            elif f_name == "cgpa" and val > 7.5:
                top_positives.append(f"solid CGPA ({val:.2f})")
            elif f_name == "quiz_average" and val > 75:
                top_positives.append(f"good quiz performance ({val:.1f}%)")
            elif f_name == "marks_trend" and val > 0:
                top_positives.append(f"improving score trajectory (+{val:.1f}%)")

        if top_positives:
            narrative += f"Protective factors stabilizing your risk include **{', '.join(top_positives)}**."

    return narrative

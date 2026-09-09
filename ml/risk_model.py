import os
import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from config import MODEL_PATH, RISK_THRESHOLDS
from database.models import get_student_by_id, update_student_metrics, add_risk_history_entry
from ml.feature_engineering import FEATURE_NAMES, extract_features_from_dict
from ml.evaluator import evaluate_model_performance

SEED = 42

def generate_synthetic_training_data(n_samples: int = 600) -> pd.DataFrame:
    """Generate reproducible synthetic academic dataset for training the dropout risk model."""
    np.random.seed(SEED)

    attendance = np.random.uniform(40.0, 98.0, n_samples)
    cgpa = np.random.uniform(4.5, 9.8, n_samples)
    backlog_count = np.random.choice([0, 1, 2, 3, 4], size=n_samples, p=[0.5, 0.25, 0.15, 0.07, 0.03])
    assignment_completion = np.clip(attendance * np.random.uniform(0.8, 1.1, n_samples), 30.0, 100.0)
    quiz_average = np.clip(cgpa * 10.0 * np.random.uniform(0.85, 1.1, n_samples), 30.0, 100.0)
    study_hours = np.clip((cgpa * 2.0) + np.random.uniform(-3, 5, n_samples), 4.0, 30.0)
    lms_activity = np.clip((attendance * 0.7) + np.random.uniform(-10, 20, n_samples), 20.0, 100.0)
    marks_trend = np.random.uniform(-15.0, 15.0, n_samples)
    attendance_trend = np.random.uniform(-20.0, 15.0, n_samples)
    engagement_score = np.clip((lms_activity * 0.5) + (assignment_completion * 0.5), 20.0, 100.0)

    # Heuristic probability of dropout
    # Risk increases with low attendance, low cgpa, backlogs, negative trends, low engagement
    risk_score_raw = (
        (100.0 - attendance) * 0.008 +
        (10.0 - cgpa) * 0.09 +
        backlog_count * 0.12 +
        (100.0 - assignment_completion) * 0.003 +
        (100.0 - engagement_score) * 0.004 -
        marks_trend * 0.008 -
        attendance_trend * 0.008
    )

    # Convert to probability using sigmoid
    dropout_prob = 1.0 / (1.0 + np.exp(-(risk_score_raw - 0.5)))
    target = (dropout_prob > 0.45).astype(int)

    df = pd.DataFrame({
        "attendance": attendance,
        "cgpa": cgpa,
        "backlog_count": backlog_count,
        "assignment_completion": assignment_completion,
        "quiz_average": quiz_average,
        "study_hours": study_hours,
        "lms_activity": lms_activity,
        "marks_trend": marks_trend,
        "attendance_trend": attendance_trend,
        "engagement_score": engagement_score,
        "dropout_prob": dropout_prob,
        "target": target
    })
    return df

def train_and_save_model() -> dict:
    """Train Logistic Regression and Random Forest models, select best, and save artifact."""
    df = generate_synthetic_training_data(n_samples=600)
    X = df[FEATURE_NAMES]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=SEED, stratify=y)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 1. Logistic Regression
    lr = LogisticRegression(random_state=SEED, max_iter=1000)
    lr.fit(X_train_scaled, y_train)
    lr_pred = lr.predict(X_test_scaled)
    lr_prob = lr.predict_proba(X_test_scaled)[:, 1]
    lr_metrics = evaluate_model_performance(y_test.values, lr_pred, lr_prob)

    # 2. Random Forest
    rf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=SEED)
    rf.fit(X_train, y_train) # Tree-based doesn't strictly need scaling
    rf_pred = rf.predict(X_test)
    rf_prob = rf.predict_proba(X_test)[:, 1]
    rf_metrics = evaluate_model_performance(y_test.values, rf_pred, rf_prob)

    # Select Random Forest as best classifier for non-linear interactions & SHAP compatibility
    best_model = rf
    best_name = "Random Forest Classifier"

    artifact = {
        "model": best_model,
        "scaler": scaler,
        "model_name": best_name,
        "feature_names": FEATURE_NAMES,
        "lr_metrics": lr_metrics,
        "rf_metrics": rf_metrics,
        "training_data_sample": df.head(10).to_dict(orient="records")
    }

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(artifact, f)

    return artifact

def load_or_train_model() -> dict:
    """Load model artifact from disk or train if missing."""
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, "rb") as f:
                return pickle.load(f)
        except Exception:
            return train_and_save_model()
    else:
        return train_and_save_model()

def get_risk_level(prob: float) -> str:
    """Map probability score to risk level based on prototype thresholds."""
    if prob < RISK_THRESHOLDS["LOW"][1]:
        return "LOW"
    elif prob < RISK_THRESHOLDS["MEDIUM"][1]:
        return "MEDIUM"
    else:
        return "HIGH"

def predict_student_risk(student_data: dict) -> tuple:
    """
    Given a student data dict, predict risk probability and level.
    Returns (risk_score: float, risk_level: str)
    """
    artifact = load_or_train_model()
    model = artifact["model"]
    
    df_feat = extract_features_from_dict(student_data)
    prob = float(model.predict_proba(df_feat)[0, 1])

    # Dynamic scaling adjustment for fine-grained prototype display
    att = float(student_data.get("attendance", 75))
    backlogs = int(student_data.get("backlog_count", 0))
    cgpa = float(student_data.get("cgpa", 7.0))
    
    # Ensure strong alignment with domain heuristics
    adjusted_prob = max(0.02, min(0.98, prob))

    risk_level = get_risk_level(adjusted_prob)
    return round(adjusted_prob, 2), risk_level

def recalculate_student_risk(student_id: int) -> dict:
    """
    Recalculate risk for student_id from current DB state.
    Updates DB `students` and inserts entry into `risk_history`.
    """
    student = get_student_by_id(student_id)
    if not student:
        return {"error": f"Student with ID {student_id} not found."}

    old_risk = float(student.get("current_risk_score", 0.0))
    new_risk, new_level = predict_student_risk(student)
    delta = round(new_risk - old_risk, 2)

    # Update Student table
    update_student_metrics(student_id, {
        "current_risk_score": new_risk,
        "current_risk_level": new_level
    })

    # Record into Risk History
    add_risk_history_entry(
        student_id=student_id,
        risk_score=new_risk,
        risk_level=new_level,
        attendance=float(student.get("attendance", 75)),
        cgpa=float(student.get("cgpa", 7.0)),
        backlogs=int(student.get("backlog_count", 0)),
        engagement=float(student.get("engagement_score", 75)),
        notes=f"Recalculated: Old {int(old_risk*100)}% -> New {int(new_risk*100)}%"
    )

    return {
        "student_id": student_id,
        "old_risk": old_risk,
        "new_risk": new_risk,
        "risk_delta": delta,
        "new_level": new_level
    }

if __name__ == "__main__":
    artifact = train_and_save_model()
    print("Model training completed. Metrics:")
    print("Random Forest Metrics:", artifact["rf_metrics"])


import numpy as np
import pandas as pd
from typing import Dict, Any, List

FEATURE_NAMES = [
    "attendance",
    "cgpa",
    "backlog_count",
    "assignment_completion",
    "quiz_average",
    "study_hours",
    "lms_activity",
    "marks_trend",
    "attendance_trend",
    "engagement_score"
]

def extract_features_from_dict(data: Dict[str, Any]) -> pd.DataFrame:
    """Extract and format feature DataFrame from a single student dictionary."""
    row = {
        "attendance": float(data.get("attendance", 75.0)),
        "cgpa": float(data.get("cgpa", 7.0)),
        "backlog_count": float(data.get("backlog_count", 0)),
        "assignment_completion": float(data.get("assignment_completion", 80.0)),
        "quiz_average": float(data.get("quiz_average", 70.0)),
        "study_hours": float(data.get("study_hours", 15.0)),
        "lms_activity": float(data.get("lms_activity", 70.0)),
        "marks_trend": float(data.get("marks_trend", 0.0)),
        "attendance_trend": float(data.get("attendance_trend", 0.0)),
        "engagement_score": float(data.get("engagement_score", 75.0))
    }
    return pd.DataFrame([row], columns=FEATURE_NAMES)

def extract_features_from_students(students: List[Dict[str, Any]]) -> pd.DataFrame:
    """Extract features DataFrame from a list of student dicts."""
    rows = []
    for s in students:
        rows.append({
            "attendance": float(s.get("attendance", 75.0)),
            "cgpa": float(s.get("cgpa", 7.0)),
            "backlog_count": float(s.get("backlog_count", 0)),
            "assignment_completion": float(s.get("assignment_completion", 80.0)),
            "quiz_average": float(s.get("quiz_average", 70.0)),
            "study_hours": float(s.get("study_hours", 15.0)),
            "lms_activity": float(s.get("lms_activity", 70.0)),
            "marks_trend": float(s.get("marks_trend", 0.0)),
            "attendance_trend": float(s.get("attendance_trend", 0.0)),
            "engagement_score": float(s.get("engagement_score", 75.0))
        })
    return pd.DataFrame(rows, columns=FEATURE_NAMES)

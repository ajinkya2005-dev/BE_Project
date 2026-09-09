import pandas as pd
from typing import List, Dict, Any
from database.models import get_student_subject_performances

def calculate_subject_level_risks(student_id: int) -> List[Dict[str, Any]]:
    """
    Retrieve and calculate subject-wise academic risk for a student.
    Does NOT simply copy overall student dropout risk; considers subject-specific marks and attendance.
    """
    performances = get_student_subject_performances(student_id)
    results = []

    for p in performances:
        marks = float(p.get("internal_marks", 70.0))
        att = float(p.get("attendance_pct", 75.0))
        assign = float(p.get("assignment_score", 75.0))

        # Subject risk formula: weighted combination of subject marks, attendance, and assignment
        subj_risk = max(0.02, min(0.98, 1.0 - ((marks / 100.0) * 0.5 + (att / 100.0) * 0.35 + (assign / 100.0) * 0.15)))
        
        if subj_risk >= 0.65:
            level = "HIGH"
        elif subj_risk >= 0.35:
            level = "MEDIUM"
        else:
            level = "LOW"

        results.append({
            "subject_id": p["subject_id"],
            "subject_code": p["subject_code"],
            "subject_name": p["subject_name"],
            "internal_marks": marks,
            "mid_term_marks": float(p.get("mid_term_marks", 65.0)),
            "assignment_score": assign,
            "attendance_pct": att,
            "risk_score": round(subj_risk, 2),
            "risk_pct": int(subj_risk * 100),
            "risk_level": level
        })

    return results

from typing import List, Dict, Any, Optional
from database.models import (
    get_interventions_for_student, get_all_interventions,
    create_intervention, update_intervention, get_student_by_id
)
from ml.risk_model import recalculate_student_risk

def initiate_student_intervention(student_id: int, faculty_id: Optional[int], title: str, description: str) -> dict:
    """Initiate a new faculty intervention for an at-risk student."""
    student = get_student_by_id(student_id)
    if not student:
        return {"error": "Student not found."}

    current_risk = float(student.get("current_risk_score", 0.25))
    cgpa = float(student.get("cgpa", 7.0))
    before_score = round(cgpa * 10.0, 1)

    intervention_id = create_intervention(
        student_id=student_id,
        faculty_id=faculty_id,
        title=title,
        description=description,
        before_score=before_score,
        before_risk=current_risk
    )

    return {
        "success": True,
        "intervention_id": intervention_id,
        "message": f"Intervention '{title}' successfully initiated for {student['full_name']}."
    }

def complete_student_intervention(intervention_id: int, student_id: int, after_score: float) -> dict:
    """Mark an intervention as completed, update outcome score, and recalculate student risk."""
    # Recalculate new risk
    recalc = recalculate_student_risk(student_id)
    new_risk = recalc.get("new_risk", 0.25)

    update_intervention(
        intervention_id=intervention_id,
        status="Completed",
        after_score=after_score,
        after_risk=new_risk
    )

    return {
        "success": True,
        "message": f"Intervention completed. After score recorded ({after_score:.0f}%). Risk updated to {int(new_risk*100)}%.",
        "new_risk": new_risk
    }

from typing import List, Dict, Any
from database.models import (
    get_student_by_id, get_all_subjects, get_study_plans_for_student,
    clear_and_add_study_plans, record_assessment
)
from analytics.subject_risk import calculate_subject_level_risks
from analytics.topic_analysis import identify_topic_weaknesses
from ocr.question_paper_ocr import compute_topic_importance_scores

def generate_personalized_study_plan(student_id: int, available_hours_daily: float = 3.0) -> List[Dict[str, Any]]:
    """
    Generate priority-weighted personalized study plan tasks based on:
    Student Risk + Subject Risk + Topic Weakness + Exam Topic Importance Score.
    """
    student = get_student_by_id(student_id)
    if not student:
        return []

    subject_risks = calculate_subject_level_risks(student_id)
    candidates = []

    for s in subject_risks:
        s_id = s["subject_id"]
        s_code = s["subject_code"]
        s_name = s["subject_name"]
        s_risk = s["risk_score"]

        # Topic weaknesses & Topic importances
        weaknesses = identify_topic_weaknesses(student_id, s_id)
        importances = compute_topic_importance_scores(s_id)
        imp_dict = {imp["topic_id"]: imp["importance_score"] for imp in importances}

        for w in weaknesses:
            t_id = w["topic_id"]
            t_name = w["topic_name"]
            score = w["score"]
            status = w["status"]
            imp_score = imp_dict.get(t_id, 50)

            # Combined Priority Score
            # High subject risk + low topic score + high exam importance = maximum priority
            priority_score = (s_risk * 40.0) + ((100.0 - score) * 0.4) + (imp_score * 0.3)

            if priority_score >= 65.0 or status == "Weak":
                priority = "HIGH"
                duration = 90
            elif priority_score >= 45.0 or status == "Moderate":
                priority = "MEDIUM"
                duration = 60
            else:
                priority = "LOW"
                duration = 45

            reason = (
                f"{priority} priority: {status} topic score ({score:.0f}%) in "
                f"{s['risk_level']}-risk subject ({s_name}) with {imp_score}/100 exam importance."
            )

            candidates.append({
                "student_id": student_id,
                "subject_id": s_id,
                "topic_id": t_id,
                "subject_name": s_name,
                "subject_code": s_code,
                "topic_name": t_name,
                "task_description": f"{s_code} ({s_name}): Study {t_name} & Solve Practice Questions",
                "duration_minutes": duration,
                "priority": priority,
                "priority_score": priority_score,
                "reason": reason,
                "status": "Not Started",
                "scheduled_date": "Today" if len(candidates) < 3 else "Tomorrow"
            })

    # Sort by priority score descending
    candidates.sort(key=lambda x: x["priority_score"], reverse=True)
    top_plans = candidates[:6]

    # Save to database
    clear_and_add_study_plans(student_id, top_plans)
    return get_study_plans_for_student(student_id)

def record_task_improvement_and_adapt(student_id: int, subject_id: int, topic_id: int, new_score: float) -> dict:
    """
    Record improved topic assessment score and trigger adaptive study plan recalculation.
    Demonstrates closed-loop adaptive planning behavior.
    """
    # 1. Save new score in assessment table
    record_assessment(
        student_id=student_id,
        subject_id=subject_id,
        topic_id=topic_id,
        assessment_name="Post-Intervention Quiz",
        max_marks=100.0,
        scored_marks=new_score,
        assessment_date="2026-09-10"
    )

    # 2. Recalculate adaptive study plan
    updated_plans = generate_personalized_study_plan(student_id)

    return {
        "success": True,
        "message": f"Recorded new topic score ({new_score:.0f}%). Adaptive planner updated target priorities.",
        "updated_plans": updated_plans
    }

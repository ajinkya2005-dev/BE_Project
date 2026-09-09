from typing import List, Dict, Any
from database.models import get_topics_for_subject, get_student_assessments

def identify_topic_weaknesses(student_id: int, subject_id: int) -> List[Dict[str, Any]]:
    """
    Identify student topic mastery levels (Strong, Moderate, Weak) for a given subject.
    Derived from student assessment scores per topic.
    """
    topics = get_topics_for_subject(subject_id)
    assessments = get_student_assessments(student_id)

    # Filter assessments for subject
    sub_assessments = [a for a in assessments if a["subject_id"] == subject_id]

    results = []
    for t in topics:
        t_id = t["id"]
        t_name = t["topic_name"]
        
        # Match topic assessment
        t_assess = [a for a in sub_assessments if a["topic_id"] == t_id]
        if t_assess:
            score = float(t_assess[0]["scored_marks"])
        else:
            # Fallback baseline score if no specific quiz recorded yet
            score = 65.0

        if score < 58.0:
            status = "Weak"
            badge_color = "red"
        elif score < 75.0:
            status = "Moderate"
            badge_color = "orange"
        else:
            status = "Strong"
            badge_color = "green"

        results.append({
            "topic_id": t_id,
            "topic_name": t_name,
            "unit_number": t.get("unit_number", 1),
            "difficulty": t.get("difficulty_level", "Medium"),
            "score": score,
            "status": status,
            "badge_color": badge_color
        })

    return results

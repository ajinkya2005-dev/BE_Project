import sqlite3
from typing import List, Dict, Any, Optional
from database.database import get_connection

# --- Student Queries ---

def get_all_students() -> List[Dict[str, Any]]:
    """Retrieve all student records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY student_code ASC;")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_student_by_id(student_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single student by primary key ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?;", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_student_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve student record associated with a user ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE user_id = ?;", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_student_metrics(student_id: int, updates: Dict[str, Any]):
    """Update student metrics (e.g. attendance, cgpa, backlogs, engagement) and updated_at."""
    if not updates:
        return
    conn = get_connection()
    cursor = conn.cursor()
    
    set_clauses = [f"{k} = ?" for k in updates.keys()]
    values = list(updates.values())
    values.append(student_id)
    
    query = f"UPDATE students SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    cursor.execute(query, values)
    conn.commit()
    conn.close()

# --- Risk History ---

def get_risk_history(student_id: int) -> List[Dict[str, Any]]:
    """Get historical risk records for a student."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM risk_history 
        WHERE student_id = ? 
        ORDER BY calculated_at ASC;
    """, (student_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def add_risk_history_entry(student_id: int, risk_score: float, risk_level: str,
                           attendance: float, cgpa: float, backlogs: int, engagement: float, notes: str = ""):
    """Record a risk score snapshot into risk_history."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO risk_history (student_id, risk_score, risk_level, attendance, cgpa, backlogs, engagement, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (student_id, risk_score, risk_level, attendance, cgpa, backlogs, engagement, notes))
    conn.commit()
    conn.close()

# --- Subjects & Performance ---

def get_all_subjects() -> List[Dict[str, Any]]:
    """Retrieve all subject records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects ORDER BY subject_code ASC;")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_student_subject_performances(student_id: int) -> List[Dict[str, Any]]:
    """Retrieve student performance joined with subject metadata."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, s.subject_code, s.subject_name, s.credits
        FROM performance p
        JOIN subjects s ON p.subject_id = s.id
        WHERE p.student_id = ?
        ORDER BY s.subject_code ASC;
    """, (student_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

# --- Topics & Question Papers ---

def get_topics_for_subject(subject_id: int) -> List[Dict[str, Any]]:
    """Get all topics for a given subject."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topics WHERE subject_id = ? ORDER BY unit_number, id;", (subject_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_question_papers_for_subject(subject_id: int) -> List[Dict[str, Any]]:
    """Get question papers for a subject."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM question_papers WHERE subject_id = ? ORDER BY year DESC;", (subject_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_questions_for_paper(paper_id: int) -> List[Dict[str, Any]]:
    """Get questions for a paper."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.*, t.topic_name 
        FROM questions q
        LEFT JOIN topics t ON q.topic_id = t.id
        WHERE q.paper_id = ?;
    """, (paper_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_all_questions_with_metadata() -> List[Dict[str, Any]]:
    """Get all questions across all papers with subject and topic names."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.*, qp.year, qp.exam_type, qp.subject_id, s.subject_name, s.subject_code, t.topic_name
        FROM questions q
        JOIN question_papers qp ON q.paper_id = qp.id
        JOIN subjects s ON qp.subject_id = s.id
        LEFT JOIN topics t ON q.topic_id = t.id;
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

# --- Study Plans ---

def get_study_plans_for_student(student_id: int) -> List[Dict[str, Any]]:
    """Get study plan entries for a student."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sp.*, s.subject_name, s.subject_code, t.topic_name
        FROM study_plans sp
        JOIN subjects s ON sp.subject_id = s.id
        JOIN topics t ON sp.topic_id = t.id
        WHERE sp.student_id = ?
        ORDER BY CASE sp.priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END, sp.id ASC;
    """, (student_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def update_study_plan_status(plan_id: int, status: str):
    """Update status of a study plan task."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE study_plans SET status = ? WHERE id = ?;", (status, plan_id))
    conn.commit()
    conn.close()

def clear_and_add_study_plans(student_id: int, plans: List[Dict[str, Any]]):
    """Replace study plans for a student with newly generated plans."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM study_plans WHERE student_id = ?;", (student_id,))
    for p in plans:
        cursor.execute("""
            INSERT INTO study_plans (student_id, subject_id, topic_id, task_description, duration_minutes, priority, reason, status, scheduled_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id, p["subject_id"], p["topic_id"], p["task_description"],
            p.get("duration_minutes", 60), p.get("priority", "MEDIUM"),
            p.get("reason", ""), p.get("status", "Not Started"), p.get("scheduled_date", "Today")
        ))
    conn.commit()
    conn.close()

# --- Interventions ---

def get_interventions_for_student(student_id: int) -> List[Dict[str, Any]]:
    """Get interventions for a given student."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, f.full_name as faculty_name 
        FROM interventions i
        LEFT JOIN faculty f ON i.faculty_id = f.id
        WHERE i.student_id = ?
        ORDER BY i.created_at DESC;
    """, (student_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_all_interventions() -> List[Dict[str, Any]]:
    """Get all interventions for faculty/admin view."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, st.full_name as student_name, st.student_code, f.full_name as faculty_name
        FROM interventions i
        JOIN students st ON i.student_id = st.id
        LEFT JOIN faculty f ON i.faculty_id = f.id
        ORDER BY i.created_at DESC;
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def create_intervention(student_id: int, faculty_id: Optional[int], title: str, description: str,
                         before_score: float, before_risk: float) -> int:
    """Create a new intervention record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO interventions (student_id, faculty_id, title, description, status, before_score, before_risk)
        VALUES (?, ?, ?, ?, 'Initiated', ?, ?)
    """, (student_id, faculty_id, title, description, before_score, before_risk))
    intervention_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return intervention_id

def update_intervention(intervention_id: int, status: str, after_score: Optional[float] = None, after_risk: Optional[float] = None):
    """Update intervention status and outcome metrics."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE interventions
        SET status = ?, after_score = COALESCE(?, after_score), after_risk = COALESCE(?, after_risk), updated_at = CURRENT_TIMESTAMP
        WHERE id = ?;
    """, (status, after_score, after_risk, intervention_id))
    conn.commit()
    conn.close()

# --- Assessments ---

def get_student_assessments(student_id: int) -> List[Dict[str, Any]]:
    """Get all topic assessment scores for a student."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, s.subject_name, s.subject_code, t.topic_name
        FROM assessments a
        JOIN subjects s ON a.subject_id = s.id
        JOIN topics t ON a.topic_id = t.id
        WHERE a.student_id = ?
        ORDER BY a.assessment_date DESC;
    """, (student_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def record_assessment(student_id: int, subject_id: int, topic_id: int, assessment_name: str, max_marks: float, scored_marks: float, assessment_date: str):
    """Record an assessment score."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assessments (student_id, subject_id, topic_id, assessment_name, max_marks, scored_marks, assessment_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (student_id, subject_id, topic_id, assessment_name, max_marks, scored_marks, assessment_date))
    conn.commit()
    conn.close()

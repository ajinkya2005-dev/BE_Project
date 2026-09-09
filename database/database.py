import sqlite3
import os
from config import DB_PATH

def get_connection():
    """Establish and return a SQLite database connection with foreign key support."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the SQLite database schema if tables do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Student', 'Faculty', 'Admin')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Students Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
        student_code TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        department TEXT NOT NULL,
        semester INTEGER NOT NULL DEFAULT 1,
        division TEXT DEFAULT 'A',
        enrollment_year INTEGER NOT NULL,
        cgpa REAL DEFAULT 7.0,
        attendance REAL DEFAULT 75.0,
        backlog_count INTEGER DEFAULT 0,
        assignment_completion REAL DEFAULT 80.0,
        quiz_average REAL DEFAULT 70.0,
        lms_activity REAL DEFAULT 70.0,
        study_hours REAL DEFAULT 15.0,
        engagement_score REAL DEFAULT 75.0,
        marks_trend REAL DEFAULT 0.0,
        attendance_trend REAL DEFAULT 0.0,
        current_risk_score REAL DEFAULT 0.25,
        current_risk_level TEXT DEFAULT 'LOW',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Faculty Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faculty (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
        faculty_code TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        department TEXT NOT NULL,
        designation TEXT NOT NULL
    );
    """)

    # 4. Subjects Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT UNIQUE NOT NULL,
        subject_name TEXT NOT NULL,
        department TEXT NOT NULL,
        semester INTEGER NOT NULL,
        credits INTEGER DEFAULT 4
    );
    """)

    # 5. Subject Performance Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
        internal_marks REAL DEFAULT 70.0,
        mid_term_marks REAL DEFAULT 70.0,
        assignment_score REAL DEFAULT 75.0,
        attendance_pct REAL DEFAULT 75.0,
        risk_score REAL DEFAULT 0.2,
        risk_level TEXT DEFAULT 'LOW',
        UNIQUE(student_id, subject_id)
    );
    """)

    # 6. Attendance Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
        date TEXT NOT NULL,
        status TEXT CHECK(status IN ('Present', 'Absent', 'Late'))
    );
    """)

    # 7. Engagement Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS engagement (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        date TEXT NOT NULL,
        lms_logins INTEGER DEFAULT 0,
        forum_posts INTEGER DEFAULT 0,
        resource_views INTEGER DEFAULT 0,
        study_minutes INTEGER DEFAULT 0
    );
    """)

    # 8. Risk History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS risk_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        risk_score REAL NOT NULL,
        risk_level TEXT NOT NULL,
        attendance REAL NOT NULL,
        cgpa REAL NOT NULL,
        backlogs INTEGER NOT NULL,
        engagement REAL NOT NULL,
        calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT
    );
    """)

    # 9. Topics Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
        topic_name TEXT NOT NULL,
        unit_number INTEGER DEFAULT 1,
        difficulty_level TEXT DEFAULT 'Medium'
    );
    """)

    # 10. Question Papers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS question_papers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
        year INTEGER NOT NULL,
        exam_type TEXT NOT NULL,
        total_marks INTEGER DEFAULT 100,
        filepath TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 11. Questions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paper_id INTEGER NOT NULL REFERENCES question_papers(id) ON DELETE CASCADE,
        topic_id INTEGER REFERENCES topics(id) ON DELETE SET NULL,
        question_number TEXT NOT NULL,
        question_text TEXT NOT NULL,
        marks INTEGER DEFAULT 5,
        unit INTEGER DEFAULT 1
    );
    """)

    # 12. Study Plans Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
        topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
        task_description TEXT NOT NULL,
        duration_minutes INTEGER DEFAULT 60,
        priority TEXT CHECK(priority IN ('HIGH', 'MEDIUM', 'LOW')),
        reason TEXT,
        status TEXT CHECK(status IN ('Not Started', 'In Progress', 'Completed')) DEFAULT 'Not Started',
        scheduled_date TEXT NOT NULL
    );
    """)

    # 13. Interventions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interventions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        faculty_id INTEGER REFERENCES faculty(id) ON DELETE SET NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT CHECK(status IN ('Proposed', 'Initiated', 'In Progress', 'Completed')) DEFAULT 'Initiated',
        before_score REAL,
        after_score REAL,
        before_risk REAL,
        after_risk REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 14. Assessments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
        topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
        assessment_name TEXT NOT NULL,
        max_marks REAL DEFAULT 100,
        scored_marks REAL DEFAULT 70,
        assessment_date TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

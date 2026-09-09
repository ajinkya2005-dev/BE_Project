import hashlib
import sqlite3
import streamlit as st
from database.database import get_connection

SALT = "EduGuard_AI_Salt_2026"

def hash_password(password: str) -> str:
    """Hash password securely using SHA-256 with a salt."""
    return hashlib.sha256((password + SALT).encode('utf-8')).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify if the entered password matches the stored hash."""
    return hash_password(password) == hashed_password

def login_user(email: str, password: str, expected_role: str):
    """
    Authenticate a user by email, password, and expected role.
    Returns (success: bool, user_data: dict, error_message: str)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return False, None, "Invalid email or user does not exist."

    user_dict = dict(user)

    if not verify_password(password, user_dict["password_hash"]):
        conn.close()
        return False, None, "Incorrect password."

    if user_dict["role"] != expected_role:
        conn.close()
        return False, None, f"Role mismatch. User is registered as {user_dict['role']}, not {expected_role}."

    # Fetch associated profile based on role
    profile = {}
    if expected_role == "Student":
        cursor.execute("SELECT * FROM students WHERE user_id = ?", (user_dict["id"],))
        res = cursor.fetchone()
        profile = dict(res) if res else {}
    elif expected_role == "Faculty":
        cursor.execute("SELECT * FROM faculty WHERE user_id = ?", (user_dict["id"],))
        res = cursor.fetchone()
        profile = dict(res) if res else {}

    conn.close()

    # Store in Streamlit session state
    st.session_state["authenticated"] = True
    st.session_state["user"] = user_dict
    st.session_state["profile"] = profile or {}
    st.session_state["role"] = expected_role

    return True, user_dict, "Login successful."

def logout_user():
    """Clear login keys from Streamlit session state."""
    st.session_state["authenticated"] = False
    st.session_state["user"] = {}
    st.session_state["profile"] = {}
    st.session_state["role"] = None
    if "selected_student_id" in st.session_state:
        del st.session_state["selected_student_id"]

def register_student(email: str, password: str, full_name: str, student_code: str,
                     department: str, semester: int, division: str, enrollment_year: int):
    """Register a new student user and create their student profile."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        pw_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (?, ?, 'Student')",
            (email.strip().lower(), pw_hash)
        )
        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO students (
                user_id, student_code, full_name, department, semester, division,
                enrollment_year, cgpa, attendance, backlog_count, assignment_completion,
                quiz_average, lms_activity, study_hours, engagement_score, current_risk_score, current_risk_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 7.5, 80.0, 0, 85.0, 75.0, 75.0, 15.0, 80.0, 0.20, 'LOW')
        """, (user_id, student_code, full_name, department, semester, division, enrollment_year))

        conn.commit()
        conn.close()
        return True, "Student registration successful. Please log in."
    except sqlite3.IntegrityError as e:
        conn.close()
        if "email" in str(e):
            return False, "An account with this email already exists."
        elif "student_code" in str(e):
            return False, "This Student ID is already registered."
        return False, f"Registration failed: {str(e)}"
    except Exception as e:
        conn.close()
        return False, f"An unexpected error occurred: {str(e)}"

def register_faculty(email: str, password: str, full_name: str, faculty_code: str,
                     department: str, designation: str):
    """Register a new faculty member."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        pw_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (?, ?, 'Faculty')",
            (email.strip().lower(), pw_hash)
        )
        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO faculty (user_id, faculty_code, full_name, department, designation)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, faculty_code, full_name, department, designation))

        conn.commit()
        conn.close()
        return True, "Faculty registration successful. Please log in."
    except sqlite3.IntegrityError as e:
        conn.close()
        if "email" in str(e):
            return False, "An account with this email already exists."
        elif "faculty_code" in str(e):
            return False, "This Faculty ID is already registered."
        return False, f"Registration failed: {str(e)}"
    except Exception as e:
        conn.close()
        return False, f"An unexpected error occurred: {str(e)}"

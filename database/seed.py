import os
import random
import sqlite3
from auth.authentication import hash_password
from database.database import get_connection, init_db
from config import DB_PATH

def seed_database(force: bool = False):
    """Seed SQLite database with 25-30 realistic student records and academic data."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM users;")
    if cursor.fetchone()[0] > 0 and not force:
        conn.close()
        return

    # Clear tables if forcing re-seed
    if force:
        tables = ["assessments", "interventions", "study_plans", "questions", "question_papers",
                  "topics", "risk_history", "engagement", "attendance", "performance",
                  "subjects", "faculty", "students", "users"]
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")
        conn.commit()

    # --- 1. Seed Users ---
    pw_student = hash_password("student123")
    pw_faculty = hash_password("faculty123")
    pw_admin = hash_password("admin123")

    # Fixed Demo Accounts
    cursor.execute("INSERT INTO users (email, password_hash, role) VALUES ('student1@eduguard.ai', ?, 'Student');", (pw_student,))
    u_stu1_id = cursor.lastrowid

    cursor.execute("INSERT INTO users (email, password_hash, role) VALUES ('faculty@eduguard.ai', ?, 'Faculty');", (pw_faculty,))
    u_fac1_id = cursor.lastrowid

    cursor.execute("INSERT INTO users (email, password_hash, role) VALUES ('admin@eduguard.ai', ?, 'Admin');", (pw_admin,))

    # Additional Faculty
    cursor.execute("INSERT INTO users (email, password_hash, role) VALUES ('prof.sharma@eduguard.ai', ?, 'Faculty');", (pw_faculty,))
    u_fac2_id = cursor.lastrowid

    # Create Faculty profiles
    cursor.execute("""
        INSERT INTO faculty (user_id, faculty_code, full_name, department, designation)
        VALUES (?, 'FAC101', 'Dr. Ramesh Kulkarni', 'Computer Engineering', 'Head of Department')
    """, (u_fac1_id,))
    fac1_db_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO faculty (user_id, faculty_code, full_name, department, designation)
        VALUES (?, 'FAC102', 'Prof. Sunita Sharma', 'Computer Engineering', 'Associate Professor')
    """, (u_fac2_id,))

    # --- 2. Seed Subjects ---
    subjects_data = [
        ("CS501", "Operating Systems", "Computer Engineering", 5, 4),
        ("CS502", "Machine Learning", "Computer Engineering", 5, 4),
        ("CS503", "Database Management Systems", "Computer Engineering", 5, 4),
        ("CS504", "Computer Networks", "Computer Engineering", 5, 3),
        ("CS505", "Applied Statistics & Probability", "Computer Engineering", 5, 3)
    ]

    subject_ids = {}
    for code, name, dept, sem, creds in subjects_data:
        cursor.execute("""
            INSERT INTO subjects (subject_code, subject_name, department, semester, credits)
            VALUES (?, ?, ?, ?, ?)
        """, (code, name, dept, sem, creds))
        subject_ids[code] = cursor.lastrowid

    # --- 3. Seed Topics ---
    topics_by_subject = {
        "CS501": [
            ("Process Synchronization & Deadlocks", 1, "Hard"),
            ("CPU Scheduling Algorithms", 2, "Medium"),
            ("Virtual Memory Management", 3, "Hard"),
            ("File System Implementation", 4, "Easy")
        ],
        "CS502": [
            ("Decision Trees & Random Forests", 1, "Medium"),
            ("Linear & Logistic Regression", 2, "Easy"),
            ("Neural Networks & Backpropagation", 3, "Hard"),
            ("K-Means & Hierarchical Clustering", 4, "Medium")
        ],
        "CS503": [
            ("Normalization (1NF to BCNF)", 1, "Hard"),
            ("SQL Queries & Subqueries", 2, "Medium"),
            ("ACID Properties & Transactions", 3, "Hard"),
            ("B-Trees & Database Indexing", 4, "Medium")
        ],
        "CS504": [
            ("TCP/IP & OSI Model Layers", 1, "Easy"),
            ("IP Subnetting & CIDR Addressing", 2, "Hard"),
            ("Distance Vector & Link State Routing", 3, "Hard"),
            ("Socket Programming & Transport Layer", 4, "Medium")
        ],
        "CS505": [
            ("Hypothesis Testing & Z/T-Tests", 1, "Hard"),
            ("Probability Distributions & Bayes Theorem", 2, "Medium"),
            ("ANOVA & Chi-Square Analysis", 3, "Hard"),
            ("Correlation & Regression Metrics", 4, "Easy")
        ]
    }

    topic_ids = {}
    for code, s_id in subject_ids.items():
        topic_ids[code] = []
        for t_name, unit, diff in topics_by_subject[code]:
            cursor.execute("""
                INSERT INTO topics (subject_id, topic_name, unit_number, difficulty_level)
                VALUES (?, ?, ?, ?)
            """, (s_id, t_name, unit, diff))
            topic_ids[code].append(cursor.lastrowid)

    # --- 4. Seed Question Papers & Questions ---
    sample_questions_pool = {
        "CS501": [
            ("Explain Bankers Algorithm for deadlock avoidance with suitable allocation matrix example.", 10, 1),
            ("Differentiate between preemptive Shortest Remaining Time First (SRTF) and Round Robin scheduling.", 8, 2),
            ("What is Demand Paging? Discuss Page Replacement Algorithms (LRU vs FIFO vs Optimal).", 10, 3),
            ("Describe inode structure in UNIX File System and direct/indirect block indexing.", 7, 4)
        ],
        "CS502": [
            ("Derive the Gini Impurity and Information Gain formula for Decision Tree splitting.", 10, 1),
            ("Explain Cost Function gradient descent formulation for Multiple Linear Regression.", 8, 2),
            ("Detail Backpropagation weight update rule using Chain Rule in Neural Networks.", 12, 3),
            ("Explain Elbow method and Silhouette score for optimal K selection in K-Means clustering.", 8, 4)
        ],
        "CS503": [
            ("Demonstrate step-by-step 3NF and BCNF decomposition of an unnormalized relation with functional dependencies.", 12, 1),
            ("Write complex SQL queries involving LEFT OUTER JOIN, GROUP BY, and HAVING clauses.", 8, 2),
            ("Explain Two-Phase Locking (2PL) Protocol and Conflict Serializability in Transaction Management.", 10, 3),
            ("Compare B+ Tree Indexing vs Hash Indexing with time complexity analysis.", 8, 4)
        ],
        "CS504": [
            ("Perform IP Subnetting: Divide 192.168.10.0/24 into 4 equal subnets and list usable host range.", 10, 2),
            ("Compare Distance Vector Routing (RIP) vs Link State Routing (OSPF) count-to-infinity problem.", 10, 3),
            ("Explain TCP 3-Way Handshake mechanism and Congestion Control window management.", 8, 4),
            ("Differentiate between IPv4 and IPv6 packet header structure.", 6, 1)
        ],
        "CS505": [
            ("Formulate Null and Alternative hypothesis to conduct a two-tailed Student t-test at 5% significance level.", 10, 1),
            ("Apply Bayes Theorem to calculate posterior disease probability given diagnostic test accuracy.", 8, 2),
            ("Perform One-Way ANOVA test to compare mean scores across three independent student cohorts.", 12, 3),
            ("Calculate Pearson correlation coefficient and linear regression slope for bivariate data.", 8, 4)
        ]
    }

    for code, s_id in subject_ids.items():
        for yr in [2023, 2024, 2025]:
            cursor.execute("""
                INSERT INTO question_papers (subject_id, year, exam_type, total_marks)
                VALUES (?, ?, 'End Semester Examination', 100)
            """, (s_id, yr))
            paper_id = cursor.lastrowid

            # Insert 4 questions per paper
            q_list = sample_questions_pool[code]
            for idx, (q_text, marks, unit) in enumerate(q_list, 1):
                top_id = topic_ids[code][(unit - 1) % len(topic_ids[code])]
                cursor.execute("""
                    INSERT INTO questions (paper_id, topic_id, question_number, question_text, marks, unit)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (paper_id, top_id, f"Q{idx}", q_text, marks, unit))

    # --- 5. Seed Students (28 Students with Realistic Profiles) ---
    students_raw = [
        # (code, name, dept, sem, cgpa, att, backlogs, assign, quiz, lms, hours, eng, risk_score, risk_level, trend_m, trend_a, is_demo)
        ("STU101", "Rohan Sharma", "Computer Engineering", 5, 5.8, 58.0, 3, 52.0, 50.0, 42.0, 8.0, 48.0, 0.78, "HIGH", -8.5, -12.0, True),
        ("STU102", "Aarav Patel", "Computer Engineering", 5, 6.1, 62.0, 2, 58.0, 55.0, 45.0, 10.0, 52.0, 0.72, "HIGH", -5.0, -8.0, False),
        ("STU103", "Ananya Verma", "Computer Engineering", 5, 5.5, 54.0, 4, 48.0, 45.0, 38.0, 6.0, 40.0, 0.85, "HIGH", -10.0, -15.0, False),
        ("STU104", "Priya Singh", "Computer Engineering", 5, 7.2, 74.0, 1, 75.0, 68.0, 68.0, 14.0, 72.0, 0.48, "MEDIUM", 1.2, -2.0, False),
        ("STU105", "Vikram Malhotra", "Computer Engineering", 5, 6.8, 70.0, 1, 70.0, 64.0, 62.0, 12.0, 66.0, 0.54, "MEDIUM", -2.0, -4.0, False),
        ("STU106", "Neha Gupta", "Computer Engineering", 5, 9.1, 92.0, 0, 95.0, 90.0, 94.0, 22.0, 92.0, 0.08, "LOW", 3.0, 2.0, False),
        ("STU107", "Siddharth Iyer", "Computer Engineering", 5, 8.8, 89.0, 0, 90.0, 86.0, 88.0, 20.0, 88.0, 0.12, "LOW", 2.0, 1.0, False),
        ("STU108", "Aditya Joshi", "Computer Engineering", 5, 6.9, 78.0, 1, 80.0, 72.0, 75.0, 16.0, 76.0, 0.38, "MEDIUM", 6.5, 10.0, False), # Improving
        ("STU109", "Riya Kapoor", "Computer Engineering", 5, 8.2, 85.0, 0, 88.0, 84.0, 48.0, 11.0, 58.0, 0.28, "LOW", 0.0, 0.0, False), # High marks low eng
        ("STU110", "Devansh Nambiar", "Computer Engineering", 5, 5.2, 50.0, 4, 42.0, 40.0, 32.0, 5.0, 35.0, 0.89, "HIGH", -12.0, -18.0, False),
        ("STU111", "Kavya Deshmukh", "Computer Engineering", 5, 7.8, 82.0, 0, 82.0, 78.0, 80.0, 18.0, 82.0, 0.22, "LOW", 1.5, 3.0, False),
        ("STU112", "Ishaan Roy", "Computer Engineering", 5, 6.4, 66.0, 2, 62.0, 60.0, 55.0, 9.0, 58.0, 0.64, "MEDIUM", -4.0, -6.0, False),
        ("STU113", "Meera Bhatt", "Computer Engineering", 5, 8.5, 88.0, 0, 92.0, 85.0, 86.0, 19.0, 89.0, 0.14, "LOW", 2.5, 1.5, False),
        ("STU114", "Karan Singhania", "Computer Engineering", 5, 5.9, 60.0, 3, 55.0, 52.0, 44.0, 7.0, 49.0, 0.76, "HIGH", -7.0, -9.0, False),
        ("STU115", "Tanvi Kulkarni", "Computer Engineering", 5, 7.4, 76.0, 0, 78.0, 74.0, 72.0, 15.0, 75.0, 0.32, "LOW", 0.5, 1.0, False),
        ("STU116", "Rahul Dravid", "Computer Engineering", 5, 6.7, 72.0, 1, 68.0, 65.0, 64.0, 13.0, 67.0, 0.52, "MEDIUM", -1.0, -2.0, False),
        ("STU117", "Shreya Ghoshal", "Computer Engineering", 5, 9.4, 96.0, 0, 98.0, 95.0, 96.0, 24.0, 95.0, 0.04, "LOW", 4.0, 3.0, False),
        ("STU118", "Manish Pandey", "Computer Engineering", 5, 5.7, 56.0, 3, 50.0, 48.0, 40.0, 6.0, 44.0, 0.81, "HIGH", -9.0, -11.0, False),
        ("STU119", "Pooja Hegde", "Computer Engineering", 5, 7.1, 75.0, 1, 74.0, 70.0, 70.0, 14.0, 71.0, 0.44, "MEDIUM", 0.0, 0.0, False),
        ("STU120", "Varun Dhawan", "Computer Engineering", 5, 6.3, 64.0, 2, 60.0, 58.0, 50.0, 8.0, 55.0, 0.67, "HIGH", -3.0, -5.0, False),
        ("STU121", "Anushka Shetty", "Computer Engineering", 5, 8.6, 90.0, 0, 91.0, 87.0, 90.0, 21.0, 90.0, 0.10, "LOW", 2.0, 2.0, False),
        ("STU122", "Yash Gowda", "Computer Engineering", 5, 5.4, 52.0, 4, 45.0, 44.0, 36.0, 5.0, 39.0, 0.87, "HIGH", -11.0, -14.0, False),
        ("STU123", "Shraddha Kapoor", "Computer Engineering", 5, 7.6, 79.0, 0, 81.0, 76.0, 78.0, 16.0, 78.0, 0.26, "LOW", 1.0, 2.0, False),
        ("STU124", "Ayushmann Khurrana", "Computer Engineering", 5, 6.9, 73.0, 1, 72.0, 67.0, 66.0, 13.0, 69.0, 0.49, "MEDIUM", 0.5, -1.0, False),
        ("STU125", "Kiara Advani", "Computer Engineering", 5, 8.9, 91.0, 0, 93.0, 89.0, 91.0, 22.0, 91.0, 0.09, "LOW", 3.0, 1.0, False),
        ("STU126", "Kartik Aaryan", "Computer Engineering", 5, 6.0, 61.0, 3, 56.0, 53.0, 43.0, 7.0, 50.0, 0.75, "HIGH", -6.0, -10.0, False),
        ("STU127", "Tripti Dimri", "Computer Engineering", 5, 7.5, 81.0, 0, 83.0, 77.0, 82.0, 17.0, 81.0, 0.24, "LOW", 2.0, 4.0, False),
        ("STU128", "Ranbir Kapoor", "Computer Engineering", 5, 6.5, 68.0, 2, 65.0, 62.0, 58.0, 10.0, 60.0, 0.59, "MEDIUM", -2.0, -3.0, False)
    ]

    student_db_ids = {}

    for item in students_raw:
        code, name, dept, sem, cgpa, att, backlogs, assign, quiz, lms, hours, eng, risk_score, risk_level, trend_m, trend_a, is_demo = item

        # User account
        if is_demo:
            u_id = u_stu1_id
        else:
            email_fake = f"{code.lower()}@eduguard.ai"
            cursor.execute("INSERT INTO users (email, password_hash, role) VALUES (?, ?, 'Student');", (email_fake, pw_student))
            u_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO students (
                user_id, student_code, full_name, department, semester, division, enrollment_year,
                cgpa, attendance, backlog_count, assignment_completion, quiz_average, lms_activity,
                study_hours, engagement_score, marks_trend, attendance_trend, current_risk_score, current_risk_level
            ) VALUES (?, ?, ?, ?, ?, 'A', 2023, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (u_id, code, name, dept, sem, cgpa, att, backlogs, assign, quiz, lms, hours, eng, trend_m, trend_a, risk_score, risk_level))
        
        st_id = cursor.lastrowid
        student_db_ids[code] = st_id

        # Seed Risk History (4 monthly snapshots showing trends)
        base_risk = risk_score
        months = ["2025-09-01", "2025-10-01", "2025-11-01", "2025-12-01"]
        if risk_level == "HIGH":
            risks = [max(0.1, base_risk - 0.25), max(0.15, base_risk - 0.18), max(0.2, base_risk - 0.08), base_risk]
            atts = [att + 18, att + 12, att + 6, att]
            engs = [eng + 20, eng + 14, eng + 7, eng]
        elif risk_level == "MEDIUM":
            risks = [0.32, 0.40, 0.45, base_risk]
            atts = [att + 10, att + 6, att + 2, att]
            engs = [eng + 10, eng + 5, eng + 2, eng]
        else:
            risks = [0.15, 0.14, 0.11, base_risk]
            atts = [att - 2, att - 1, att, att]
            engs = [eng - 2, eng - 1, eng, eng]

        for m_idx, m_date in enumerate(months):
            cursor.execute("""
                INSERT INTO risk_history (student_id, risk_score, risk_level, attendance, cgpa, backlogs, engagement, calculated_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Monthly automated assessment')
            """, (st_id, round(risks[m_idx], 2), "HIGH" if risks[m_idx] >= 0.65 else ("MEDIUM" if risks[m_idx] >= 0.35 else "LOW"),
                  round(atts[m_idx], 1), cgpa, backlogs, round(engs[m_idx], 1), m_date))

        # Seed Subject Performance per student
        for s_code, s_id in subject_ids.items():
            # Create variation per subject
            s_mult = random.uniform(0.85, 1.15) if not is_demo else (0.6 if s_code in ["CS501", "CS502"] else 0.8)
            s_marks = round(min(98.0, max(35.0, cgpa * 10.0 * s_mult)), 1)
            s_att = round(min(100.0, max(40.0, att * s_mult)), 1)
            s_risk = round(max(0.05, min(0.95, 1.0 - (s_marks / 100.0 * 0.6 + s_att / 100.0 * 0.4))), 2)
            s_level = "HIGH" if s_risk >= 0.65 else ("MEDIUM" if s_risk >= 0.35 else "LOW")

            cursor.execute("""
                INSERT INTO performance (student_id, subject_id, internal_marks, mid_term_marks, assignment_score, attendance_pct, risk_score, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (st_id, s_id, s_marks, s_marks - 5, assign * s_mult, s_att, s_risk, s_level))

            # Seed Topic Assessments
            for t_id in topic_ids[s_code]:
                scored = round(min(100.0, max(30.0, s_marks * random.uniform(0.75, 1.1))), 1)
                cursor.execute("""
                    INSERT INTO assessments (student_id, subject_id, topic_id, assessment_name, max_marks, scored_marks, assessment_date)
                    VALUES (?, ?, ?, 'Unit Quiz', 100, ?, '2025-11-20')
                """, (st_id, s_id, t_id, scored))

    # --- 6. Seed Demo Student Study Plan & Interventions ---
    demo_st_id = student_db_ids["STU101"]
    cs501_id = subject_ids["CS501"]
    cs502_id = subject_ids["CS502"]
    cs503_id = subject_ids["CS503"]

    os_deadlock_tid = topic_ids["CS501"][0]
    ml_dt_tid = topic_ids["CS502"][0]
    dbms_norm_tid = topic_ids["CS503"][0]

    study_tasks = [
        (demo_st_id, cs501_id, os_deadlock_tid, "Operating Systems: Practice Deadlock Avoidance & Bankers Algorithm", 90, "HIGH", "Weak topic in high-risk subject with 92% exam importance", "Not Started", "Today"),
        (demo_st_id, cs503_id, dbms_norm_tid, "DBMS: Solve 3NF & BCNF Decomposition Problems", 60, "HIGH", "High priority weak topic in DBMS with high exam weightage", "In Progress", "Today"),
        (demo_st_id, cs502_id, ml_dt_tid, "Machine Learning: Review Decision Tree Gini Impurity Calculations", 60, "MEDIUM", "Core foundational topic requiring revision", "Not Started", "Tomorrow")
    ]

    for st_id, s_id, t_id, desc, dur, prio, reas, stat, s_date in study_tasks:
        cursor.execute("""
            INSERT INTO study_plans (student_id, subject_id, topic_id, task_description, duration_minutes, priority, reason, status, scheduled_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (st_id, s_id, t_id, desc, dur, prio, reas, stat, s_date))

    # Seed Interventions for STU101
    cursor.execute("""
        INSERT INTO interventions (student_id, faculty_id, title, description, status, before_score, after_score, before_risk, after_risk)
        VALUES (?, ?, 'DBMS Normalization & Deadlocks Remedial Workshop', 'Assigned 1-on-1 tutoring sessions and specialized problem sets for Operating Systems and DBMS normalization.', 'Initiated', 45.0, NULL, 0.78, NULL)
    """, (demo_st_id, fac1_db_id))

    conn.commit()
    conn.close()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database(force=True)

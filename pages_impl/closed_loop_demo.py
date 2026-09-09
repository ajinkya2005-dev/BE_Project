import streamlit as st
import pandas as pd
from database.models import get_student_by_id, get_all_students, update_student_metrics
from ml.risk_model import recalculate_student_risk, predict_student_risk
from xai.explainer import compute_shap_explanations
from analytics.subject_risk import calculate_subject_level_risks
from analytics.topic_analysis import identify_topic_weaknesses
from ocr.question_paper_ocr import compute_topic_importance_scores
from planner.study_planner import generate_personalized_study_plan, record_task_improvement_and_adapt
from utils.styling import render_metric_card, render_status_pill
from utils.helpers import render_alert_box

def render_closed_loop_demo():
    """Render Dedicated 10-Step Closed-Loop Architecture Workflow Demo."""
    st.markdown('<div class="header-title">Closed-Loop AI Intelligence Demo</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">Interactive 10-step demonstration of EduGuard AI closed-loop workflow</div>', unsafe_allow_html=True)

    render_alert_box(
        "🔄 <b>CORE RESEARCH CONCEPT:</b> EduGuard AI is built around a closed-loop feedback pipeline: "
        "<b>Predict ➔ Explain ➔ Identify Weakness ➔ Mine Exam Importance ➔ Plan ➔ Intervene ➔ Monitor Progress ➔ Recalculate Risk ➔ Adapt Plan</b>. "
        "Use the controls below to select demo profiles and simulate live score/attendance improvements!",
        severity="info"
    )

    # Demo Student Preset Selector
    all_students = get_all_students()
    demo_options = {
        "STU101 — Rohan Sharma (High Risk: 78%)": 1,
        "STU102 — Aarav Patel (High Risk: 72%)": 2,
        "STU104 — Priya Singh (Medium Risk: 48%)": 4,
        "STU108 — Aditya Joshi (Improving Student)": 8,
        "STU106 — Neha Gupta (Low Risk: 8%)": 6
    }

    sel_label = st.selectbox("🎯 Select Demo Student Profile to Load into Pipeline", list(demo_options.keys()))
    student_id = demo_options[sel_label]
    student = get_student_by_id(student_id)

    if not student:
        st.error("Student profile not found.")
        return

    # Store override student ID in session state for cross-page consistency
    st.session_state["override_student_id"] = student_id

    st.markdown("---")

    # Step 1 & 2: Student Data & Risk Prediction
    c_s1, c_s2 = st.columns([0.45, 0.55])

    with c_s1:
        st.markdown("#### 1️⃣ STEP 1: Student Data & Indicators")
        st.write(f"**Name:** {student['full_name']} ({student['student_code']})")
        st.write(f"• Attendance: **{student['attendance']:.1f}%**")
        st.write(f"• CGPA: **{student['cgpa']:.2f}** / 10.0")
        st.write(f"• Active Backlogs: **{int(student['backlog_count'])}**")
        st.write(f"• Assignment Completion: **{student['assignment_completion']:.0f}%**")
        st.write(f"• LMS Engagement Score: **{student['engagement_score']:.0f}%**")

    with c_s2:
        st.markdown("#### 2️⃣ STEP 2: Risk Prediction Model")
        r_score = float(student["current_risk_score"])
        r_level = student["current_risk_level"]
        r_pct = int(r_score * 100)

        bg_c = "#FEF2F2" if r_level == "HIGH" else ("#FFFBEB" if r_level == "MEDIUM" else "#ECFDF5")
        st.markdown(f"""
        <div style="background: {bg_c}; border-left: 5px solid {'#EF4444' if r_level=='HIGH' else ('#F59E0B' if r_level=='MEDIUM' else '#10B981')}; padding: 18px; border-radius: 10px; border: 1px solid #E2E8F0;">
            <div style="font-size: 0.9rem; font-weight: 700; color: #64748B;">DROPOUT RISK PROBABILITY</div>
            <div style="font-size: 2.2rem; font-weight: 800; color: #0F172A;">{r_pct}%</div>
            <div>{render_status_pill(r_level)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Step 3 & 4: XAI Explanation & Weak Areas
    c_s3, c_s4 = st.columns(2)

    with c_s3:
        st.markdown("#### 3️⃣ STEP 3: SHAP XAI Explanation")
        shap_res = compute_shap_explanations(student)
        st.write(shap_res["summary_narrative"])

    with c_s4:
        st.markdown("#### 4️⃣ STEP 4: Weak Area Identification")
        sub_risks = calculate_subject_level_risks(student_id)
        for s in sub_risks[:3]:
            weaknesses = identify_topic_weaknesses(student_id, s["subject_id"])
            weak_topics = [w["topic_name"] for w in weaknesses if w["status"] == "Weak"]
            weak_str = ", ".join(weak_topics) if weak_topics else "None"
            st.write(f"• **{s['subject_code']} ({s['risk_level']} Risk):** Weak Topics: *{weak_str}*")

    st.markdown("---")

    # Step 5 & 6: Question Intelligence & Personalized Study Plan
    c_s5, c_s6 = st.columns(2)

    with c_s5:
        st.markdown("#### 5️⃣ STEP 5: Exam Question Intelligence")
        st.caption("Top Mined Topic Importance Scores:")
        top_imps = compute_topic_importance_scores(sub_risks[0]["subject_id"]) if sub_risks else []
        for imp in top_imps[:3]:
            st.write(f"• **{imp['topic_name']}:** Importance Score **{imp['importance_score']}/100** ({imp['frequency']} questions in past exams)")

    with c_s6:
        st.markdown("#### 6️⃣ STEP 6: Personalized Study Plan")
        plans = generate_personalized_study_plan(student_id)
        for p in plans[:3]:
            st.write(f"• **{p['subject_code']} ({p['topic_name']}):** {p['duration_minutes']} mins — *{p['priority']} Priority*")

    st.markdown("---")

    # Step 7, 8, 9, 10: Intervention, Progress, Recalculation & Adaptation
    st.markdown("#### 🚀 STEPS 7–10: Simulate Student Improvement & Closed-Loop Adaptation")

    sim_col1, sim_col2 = st.columns(2)

    with sim_col1:
        st.markdown("##### ⚡ Interactive Improvement Simulator:")
        new_att = st.slider("Simulate Improved Attendance (%)", min_value=float(student["attendance"]), max_value=95.0, value=min(90.0, float(student["attendance"]) + 15.0), step=1.0)
        new_assign = st.slider("Simulate Improved Assignments (%)", min_value=float(student["assignment_completion"]), max_value=98.0, value=min(95.0, float(student["assignment_completion"]) + 20.0), step=1.0)
        new_quiz = st.slider("Simulate Improved Quiz Average (%)", min_value=float(student["quiz_average"]), max_value=95.0, value=min(90.0, float(student["quiz_average"]) + 25.0), step=1.0)

        if st.button("✨ Apply Improvements & Recalculate Closed-Loop Risk", use_container_width=True):
            # Update Student metrics
            update_student_metrics(student_id, {
                "attendance": new_att,
                "assignment_completion": new_assign,
                "quiz_average": new_quiz,
                "engagement_score": min(95.0, new_att * 0.5 + new_assign * 0.5)
            })

            # Recalculate Risk
            res = recalculate_student_risk(student_id)

            # Record quiz improvement for weak topic
            if sub_risks:
                record_task_improvement_and_adapt(student_id, sub_risks[0]["subject_id"], top_imps[0]["topic_id"], new_quiz)

            st.balloons()
            st.success(f"🎉 Risk Recalculated! Old: {int(res['old_risk']*100)}% ➔ New Risk: {int(res['new_risk']*100)}% ({res['new_level']})")
            st.rerun()

    with sim_col2:
        st.markdown("##### 📊 Closed-Loop Workflow Flowchart:")
        st.markdown("""
        ```mermaid
        graph TD
            A[Student Academic Data] --> B[Dropout Risk Prediction Model]
            B --> C[SHAP Feature Attribution XAI]
            C --> D[Weak Subject & Topic Discovery]
            D --> E[OCR Question Paper Intelligence]
            E --> F[Personalized Priority Study Plan]
            F --> G[Faculty Intervention & Tutoring]
            G --> H[Student Progress & Quiz Updates]
            H -->|Closed-Loop Feedback| B
        ```
        """, unsafe_allow_html=True)

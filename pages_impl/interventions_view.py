import streamlit as st
import pandas as pd
from database.models import (
    get_all_interventions, get_interventions_for_student,
    get_all_students, get_student_by_id, get_student_by_user_id
)
from intervention.intervention_tracker import initiate_student_intervention, complete_student_intervention
from utils.styling import render_status_pill
from utils.helpers import render_alert_box

def render_interventions_view():
    """Render Faculty & Student Interventions Tracking Page."""
    user = st.session_state.get("user") or {}
    role = st.session_state.get("role") or "Student"
    profile = st.session_state.get("profile") or {}
    if not profile:
        profile = get_student_by_user_id(user.get("id", 1)) or {}

    st.markdown('<div class="header-title">Academic Intervention Tracking</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">Initiate, monitor, and evaluate remedial academic intervention workflows</div>', unsafe_allow_html=True)

    if role in ["Faculty", "Admin"]:
        tab_active, tab_new = st.tabs(["📋 Active Interventions Directory", "➕ Initiate New Intervention"])

        with tab_active:
            st.markdown("### 🔍 All Institutional Interventions")
            interventions = get_all_interventions()

            if interventions:
                df_int = pd.DataFrame(interventions)
                df_display = df_int.rename(columns={
                    "student_code": "Student ID",
                    "student_name": "Student Name",
                    "faculty_name": "Assigned Faculty",
                    "title": "Intervention Title",
                    "status": "Status",
                    "before_risk": "Before Risk",
                    "after_risk": "After Risk",
                    "created_at": "Initiated Date"
                })

                st.dataframe(df_display[["Student ID", "Student Name", "Assigned Faculty", "Intervention Title", "Status", "Before Risk", "After Risk", "Initiated Date"]], use_container_width=True)

                st.markdown("---")
                st.markdown("#### ⚡ Complete Intervention Action")
                selected_int_id = st.selectbox("Select Active Intervention to Mark Completed", [i["id"] for i in interventions if i["status"] != "Completed"])
                after_score = st.slider("Outcome Assessment Score (%)", min_value=50, max_value=98, value=82, step=2)

                if st.button("Mark Completed & Recalculate Risk", use_container_width=True):
                    matched_int = next((i for i in interventions if i["id"] == selected_int_id), None)
                    if matched_int:
                        res = complete_student_intervention(selected_int_id, matched_int["student_id"], after_score)
                        st.success(res["message"])
                        st.rerun()
            else:
                st.info("No active interventions recorded.")

        with tab_new:
            st.markdown("### ➕ Assign Remedial Intervention")
            students = get_all_students()
            at_risk = [s for s in students if s["current_risk_level"] in ["HIGH", "MEDIUM"]]

            if at_risk:
                stu_dict = {f"{s['student_code']} - {s['full_name']} (Risk: {int(s['current_risk_score']*100)}% {s['current_risk_level']})": s["id"] for s in at_risk}
                sel_stu_label = st.selectbox("Target At-Risk Student", list(stu_dict.keys()))
                target_st_id = stu_dict[sel_stu_label]

                title = st.text_input("Intervention Title", value="DBMS & Operating Systems Remedial Workshop")
                desc = st.text_area("Description & Action Plan", value="Assigned 1-on-1 peer mentoring sessions and specialized problem sets focusing on Normalization and Deadlocks.")

                if st.button("Initiate Intervention Plan", use_container_width=True):
                    faculty_id = profile.get("id", 1) if role == "Faculty" else None
                    res = initiate_student_intervention(target_st_id, faculty_id, title, desc)
                    st.success(res["message"])
                    st.rerun()
            else:
                st.info("No high/medium risk students currently require intervention.")

    else:
        # Student View
        student_id = profile.get("id", 1)
        if "override_student_id" in st.session_state:
            student_id = st.session_state["override_student_id"]

        st.markdown("### 📋 My Active Interventions & Mentoring Plans")
        interventions = get_interventions_for_student(student_id)

        if interventions:
            for item in interventions:
                st.markdown(f"""
                <div style="background: white; border-left: 5px solid #4F46E5; padding: 18px; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 14px;">
                    <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A;">{item['title']}</div>
                    <div style="font-size: 0.85rem; color: #64748B; margin-top: 2px;">Assigned Faculty: <b>{item.get('faculty_name', 'HOD Computer Engg')}</b> | Status: <b>{item['status']}</b></div>
                    <p style="color: #334155; margin-top: 8px;">{item['description']}</p>
                    <div style="display: flex; gap: 16px; margin-top: 10px; font-size: 0.88rem;">
                        <span>Risk Before: <b>{int((item['before_risk'] or 0.78)*100)}%</b></span>
                        <span>Risk After: <b>{int((item['after_risk'] or item['before_risk'] or 0.78)*100)}%</b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("You currently have no active intervention actions assigned.")

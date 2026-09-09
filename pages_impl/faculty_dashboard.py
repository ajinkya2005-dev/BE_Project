import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.models import (
    get_all_students, get_student_by_id, get_all_subjects,
    get_interventions_for_student
)
from analytics.subject_risk import calculate_subject_level_risks
from analytics.topic_analysis import identify_topic_weaknesses
from xai.explainer import compute_shap_explanations
from intervention.intervention_tracker import initiate_student_intervention
from utils.styling import render_metric_card, render_status_pill
from utils.helpers import convert_df_to_csv, render_alert_box

def render_faculty_dashboard():
    """Render Faculty & Admin Risk Monitoring Dashboard."""
    user = st.session_state.get("user") or {}
    profile = st.session_state.get("profile") or {}
    name = profile.get("full_name") or user.get("email", "Faculty Advisor")

    st.markdown(f'<div class="header-title">Faculty Cohort Risk Monitoring — Welcome, {name}</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">Institutional student dropout risk analytics, early warning surveillance, and intervention management</div>', unsafe_allow_html=True)

    students = get_all_students()
    if not students:
        st.warning("No student records found in database.")
        return

    df_stu = pd.DataFrame(students)
    df_stu["risk_pct"] = (df_stu["current_risk_score"] * 100).round(0).astype(int)

    # 1. Cohort KPIs (2 Rows of 3 Columns for Spacious Non-Overlapping Cards)
    total_st = len(df_stu)
    high_cnt = len(df_stu[df_stu["current_risk_level"] == "HIGH"])
    med_cnt = len(df_stu[df_stu["current_risk_level"] == "MEDIUM"])
    low_cnt = len(df_stu[df_stu["current_risk_level"] == "LOW"])
    avg_att = df_stu["attendance"].mean()
    avg_eng = df_stu["engagement_score"].mean()

    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Total Students", f"{total_st}", "Enrolled Cohort")
    with c2:
        render_metric_card("High Risk Students", f"{high_cnt}", f"{(high_cnt/total_st)*100:.0f}% of cohort", risk_level="HIGH")
    with c3:
        render_metric_card("Medium Risk Students", f"{med_cnt}", f"{(med_cnt/total_st)*100:.0f}% of cohort", risk_level="MEDIUM")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3)
    with c4:
        render_metric_card("Low Risk Students", f"{low_cnt}", f"{(low_cnt/total_st)*100:.0f}% of cohort", risk_level="LOW")
    with c5:
        render_metric_card("Average Attendance", f"{avg_att:.1f}%", "Cohort Mean")
    with c6:
        render_metric_card("Average Engagement", f"{avg_eng:.0f}%", "Portal Activity Score")

    st.markdown("---")

    # 2. Charts Section
    col_ch1, col_ch2 = st.columns(2)

    with col_ch1:
        st.markdown("#### 🍩 Risk Category Distribution")
        fig_donut = px.pie(
            df_stu,
            names="current_risk_level",
            title="Cohort Risk Categorization",
            color="current_risk_level",
            color_discrete_map={"HIGH": "#EF4444", "MEDIUM": "#F59E0B", "LOW": "#10B981"},
            hole=0.45
        )
        fig_donut.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", color="#0F172A")
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_ch2:
        st.markdown("#### 📊 CGPA vs Attendance Risk Matrix")
        fig_scatter = px.scatter(
            df_stu,
            x="attendance",
            y="cgpa",
            color="current_risk_level",
            size="risk_pct",
            hover_name="full_name",
            color_discrete_map={"HIGH": "#EF4444", "MEDIUM": "#F59E0B", "LOW": "#10B981"},
            title="Attendance vs CGPA Distribution"
        )
        fig_scatter.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", color="#0F172A")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

    # 3. Filterable Student Directory Table
    st.markdown("### 🎓 Student Directory & Risk Assessment Table")

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        risk_filter = st.multiselect("Filter by Risk Level", ["HIGH", "MEDIUM", "LOW"], default=["HIGH", "MEDIUM", "LOW"])
    with f_col2:
        dept_filter = st.selectbox("Department Filter", ["All Departments"] + list(df_stu["department"].unique()))
    with f_col3:
        search_query = st.text_input("Search Student Name or ID", "")

    # Apply filters
    df_filtered = df_stu[df_stu["current_risk_level"].isin(risk_filter)].copy()
    if dept_filter != "All Departments":
        df_filtered = df_filtered[df_filtered["department"] == dept_filter]
    if search_query:
        df_filtered = df_filtered[
            df_filtered["full_name"].str.contains(search_query, case=False) |
            df_filtered["student_code"].str.contains(search_query, case=False)
        ]

    # Export CSV Button
    csv_bytes = convert_df_to_csv(df_filtered[["student_code", "full_name", "department", "semester", "cgpa", "attendance", "backlog_count", "risk_pct", "current_risk_level"]])
    st.download_button("📥 Export Student Risk Summary CSV", data=csv_bytes, file_name="eduguard_student_risk_report.csv", mime="text/csv")

    st.dataframe(
        df_filtered[["student_code", "full_name", "department", "semester", "cgpa", "attendance", "backlog_count", "risk_pct", "current_risk_level"]].rename(columns={
            "student_code": "Student ID",
            "full_name": "Full Name",
            "department": "Department",
            "semester": "Sem",
            "cgpa": "CGPA",
            "attendance": "Attendance %",
            "backlog_count": "Backlogs",
            "risk_pct": "Risk %",
            "current_risk_level": "Risk Level"
        }),
        use_container_width=True
    )

    # 4. Student Detail Drill-Down Modal / Section
    st.markdown("---")
    st.markdown("### 🔍 Student Detailed Intelligence Drill-Down")

    selected_student_code = st.selectbox(
        "Select Student for In-Depth Profile & SHAP XAI Breakdown",
        options=df_filtered["student_code"].tolist() if not df_filtered.empty else df_stu["student_code"].tolist()
    )

    if selected_student_code:
        st_row = df_stu[df_stu["student_code"] == selected_student_code].iloc[0].to_dict()
        s_id = st_row["id"]

        st.markdown(f"#### 👤 Student Profile: **{st_row['full_name']}** ({st_row['student_code']})")

        d_c1, d_c2, d_c3, d_c4 = st.columns(4)
        with d_c1:
            st.metric("Dropout Risk", f"{st_row['risk_pct']}%", delta=f"{st_row['current_risk_level']}")
        with d_c2:
            st.metric("Attendance", f"{st_row['attendance']:.1f}%")
        with d_c3:
            st.metric("CGPA", f"{st_row['cgpa']:.2f}")
        with d_c4:
            st.metric("Active Backlogs", f"{st_row['backlog_count']}")

        # SHAP XAI for selected student
        shap_res = compute_shap_explanations(st_row)
        render_alert_box(f"<b>SHAP XAI Explanation:</b> {shap_res['summary_narrative']}", severity="info")

        # Subject Level Risks
        sub_risks = calculate_subject_level_risks(s_id)
        st.markdown("##### 📚 Subject-Specific Performance & Risks:")
        df_sub = pd.DataFrame(sub_risks)
        st.dataframe(df_sub[["subject_code", "subject_name", "internal_marks", "attendance_pct", "risk_pct", "risk_level"]], use_container_width=True)

        # Quick Initiate Intervention
        with st.expander(f"➕ Initiate Quick Intervention for {st_row['full_name']}"):
            int_title = st.text_input("Intervention Title", value=f"Remedial Support for {st_row['full_name']}", key="fac_int_t")
            int_desc = st.text_area("Remedial Action Plan", value="Mandatory 1-on-1 tutoring sessions and weekly problem set reviews.", key="fac_int_d")
            if st.button("Submit Intervention Plan", key="btn_quick_int"):
                faculty_id = profile.get("id") or 1
                res = initiate_student_intervention(s_id, faculty_id, int_title, int_desc)
                st.success(res["message"])
                st.rerun()

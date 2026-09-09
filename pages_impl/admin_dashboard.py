import streamlit as st
import pandas as pd
import plotly.express as px
from database.models import get_all_students, get_all_subjects, get_all_interventions
from database.seed import seed_database
from utils.styling import render_metric_card
from utils.helpers import render_alert_box

def render_admin_dashboard():
    """Render Admin System Overview Dashboard."""
    st.markdown('<div class="header-title">System Administration & Analytics Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">System-level metrics, database administration, and institutional risk oversight</div>', unsafe_allow_html=True)

    students = get_all_students()
    subjects = get_all_subjects()
    interventions = get_all_interventions()

    df_stu = pd.DataFrame(students) if students else pd.DataFrame()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Total Registered Students", f"{len(students)}")
    with c2:
        render_metric_card("Active Subjects", f"{len(subjects)}")
    with c3:
        render_metric_card("Interventions Logged", f"{len(interventions)}")
    with c4:
        high_cnt = len(df_stu[df_stu["current_risk_level"] == "HIGH"]) if not df_stu.empty else 0
        render_metric_card("High-Risk Count", f"{high_cnt}", risk_level="HIGH")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 Institutional Risk Profile Distribution")
        if not df_stu.empty:
            fig_hist = px.histogram(df_stu, x="current_risk_score", nbins=10, title="Risk Score Frequency Distribution", color="current_risk_level")
            fig_hist.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        st.markdown("#### 🛠️ Database & Prototype Controls")
        render_alert_box("⚠️ <b>Admin Maintenance Action:</b> Re-seeding database will reset all student metrics and interventions to baseline demo state.", severity="warning")

        if st.button("🔄 Force Re-Seed Database (Restore Demo State)", use_container_width=True):
            seed_database(force=True)
            st.success("Database re-seeded successfully.")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Student Directory Master List")
    if not df_stu.empty:
        st.dataframe(df_stu[["student_code", "full_name", "department", "semester", "cgpa", "attendance", "current_risk_score", "current_risk_level"]], use_container_width=True)

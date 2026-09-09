import streamlit as st
import pandas as pd
from database.models import get_student_by_id, get_student_by_user_id
from analytics.longitudinal import get_longitudinal_trends
from analytics.subject_risk import calculate_subject_level_risks
from ml.risk_model import recalculate_student_risk
from utils.styling import (
    render_metric_card, render_status_pill,
    create_risk_gauge_chart, create_trend_line_chart
)
from utils.helpers import render_alert_box, format_percentage

def render_student_dashboard():
    """Render Student Personalized Dashboard."""
    user = st.session_state.get("user") or {}
    profile = st.session_state.get("profile") or {}

    if not profile:
        profile = get_student_by_user_id(user.get("id", 1)) or {}

    student_id = profile.get("id", 1)

    # Allow selecting demo student override if set in session state
    if "override_student_id" in st.session_state:
        student_id = st.session_state["override_student_id"]
        profile = get_student_by_id(student_id) or profile

    name = profile.get("full_name", "Student")
    dept = profile.get("department", "Computer Engineering")
    sem = profile.get("semester", 5)

    st.markdown(f'<div class="header-title">Good morning, {name} 👋</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="header-subtitle">{dept} • Semester {sem} • Student ID: {profile.get("student_code", "STU101")}</div>', unsafe_allow_html=True)

    # 1. Early Warning Banner System
    risk_score = float(profile.get("current_risk_score", 0.25))
    risk_level = profile.get("current_risk_level", "LOW")
    risk_pct = int(risk_score * 100)

    if risk_level == "HIGH":
        render_alert_box(
            f"🚨 <b>CRITICAL RISK ALERT:</b> Your academic risk index is elevated at <b>{risk_pct}% ({risk_level})</b>. "
            f"Please review your <b>Why am I at risk? (SHAP XAI)</b> breakdown and complete daily tasks in your <b>Study Planner</b>.",
            severity="critical"
        )
    elif risk_level == "MEDIUM":
        render_alert_box(
            f"⚠️ <b>WARNING:</b> Academic risk level is currently <b>{risk_pct}% ({risk_level})</b>. "
            f"Improving attendance and completing upcoming quizzes will help lower your risk category.",
            severity="warning"
        )
    else:
        render_alert_box(
            f"✅ <b>EXCELLENT STANDING:</b> Academic risk is low at <b>{risk_pct}%</b>. Keep up the consistent study routine!",
            severity="info"
        )

    # 2. KPI Metrics Grid (Spacious 2-Row Layout)
    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Dropout Risk", f"{risk_pct}%", f"Category: {risk_level}", risk_level=risk_level)
    with c2:
        render_metric_card("CGPA Score", f"{profile.get('cgpa', 7.0):.2f}", "Scale: 10.0")
    with c3:
        render_metric_card("Attendance Rate", f"{profile.get('attendance', 75.0):.1f}%", "Target: >= 75%")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    c4, c5 = st.columns(2)
    with c4:
        render_metric_card("LMS Engagement Index", f"{profile.get('engagement_score', 75.0):.0f}%", "Composite Activity")
    with c5:
        render_metric_card("Active Backlogs Count", f"{int(profile.get('backlog_count', 0))}", "Pending Coursework")

    st.markdown("---")

    # 3. Main Dashboard Visuals (Risk Gauge & Longitudinal Trends)
    col_g, col_t = st.columns([0.45, 0.55])

    with col_g:
        st.markdown("#### 🎯 Current Risk Assessment")
        fig_gauge = create_risk_gauge_chart(risk_score)
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Quick Action Button to recalculate risk
        if st.button("🔄 Recalculate Risk Index Live", use_container_width=True):
            res = recalculate_student_risk(student_id)
            st.toast(f"Risk updated: {int(res['old_risk']*100)}% ➔ {int(res['new_risk']*100)}%")
            st.session_state["profile"] = get_student_by_id(student_id)
            st.rerun()

    with col_t:
        st.markdown("#### 📈 Longitudinal Risk & Academic Trajectory")
        df_history = get_longitudinal_trends(student_id)
        if not df_history.empty:
            fig_trend = create_trend_line_chart(df_history, "calculated_at", "risk_pct", "Historical Dropout Risk Score (%)")
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No historical risk snapshots recorded yet.")

    # 4. Subject-Wise Risk Summary
    st.markdown("---")
    st.markdown("#### 📚 Subject Risk Overview")
    subject_risks = calculate_subject_level_risks(student_id)

    cols = st.columns(len(subject_risks) if subject_risks else 1)
    for idx, s in enumerate(subject_risks):
        with cols[idx % len(cols)]:
            s_lvl = s["risk_level"]
            s_pct = s["risk_pct"]
            bg_clr = "#FEF2F2" if s_lvl == "HIGH" else ("#FFFBEB" if s_lvl == "MEDIUM" else "#ECFDF5")

            st.markdown(f"""
            <div style="background: {bg_clr}; border-radius: 10px; padding: 14px; border: 1px solid #E2E8F0;">
                <div style="font-weight: 700; font-size: 0.95rem; color: #0F172A;">{s['subject_code']}</div>
                <div style="font-size: 0.8rem; color: #334155; margin-bottom: 6px;">{s['subject_name']}</div>
                <div style="font-size: 1.3rem; font-weight: 800; color: #0F172A;">{s_pct}%</div>
                <div style="margin-top: 4px;">{render_status_pill(s_lvl)}</div>
            </div>
            """, unsafe_allow_html=True)

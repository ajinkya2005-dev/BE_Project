import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from database.models import get_student_by_id, get_student_by_user_id
from xai.explainer import compute_shap_explanations
from utils.styling import render_status_pill

def render_risk_analysis_page():
    """Render SHAP Explainable AI (XAI) Risk Analysis view."""
    user = st.session_state.get("user") or {}
    profile = st.session_state.get("profile") or {}
    if not profile:
        profile = get_student_by_user_id(user.get("id", 1)) or {}

    student_id = profile.get("id", 1)
    if "override_student_id" in st.session_state:
        student_id = st.session_state["override_student_id"]
        profile = get_student_by_id(student_id) or profile

    name = profile.get("full_name", "Student")
    risk_score = float(profile.get("current_risk_score", 0.25))
    risk_level = profile.get("current_risk_level", "LOW")
    risk_pct = int(risk_score * 100)

    st.markdown(f'<div class="header-title">Why am I at Risk? — SHAP XAI Explanation</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="header-subtitle">Transparent feature attribution explaining factors driving academic risk for {name}</div>', unsafe_allow_html=True)

    # 1. Compute SHAP Explanation
    shap_results = compute_shap_explanations(profile)
    summary_text = shap_results["summary_narrative"]
    df_exp = shap_results["explanation_df"]
    risk_drivers = shap_results["risk_drivers"]
    protective = shap_results["protective_factors"]

    # 2. Human-Readable Explanation Box
    st.markdown(f"""
    <div style="background: white; padding: 20px; border-radius: 12px; border-left: 5px solid #4F46E5; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 24px;">
        <h4 style="margin-top: 0; color: #4F46E5;">💡 Plain-Language Academic Risk Explanation</h4>
        <p style="font-size: 1.05rem; line-height: 1.6; color: #1E293B;">{summary_text}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([0.65, 0.35])

    with col1:
        st.markdown("### 📊 SHAP Feature Attribution Impact")
        st.caption("Positive values increase risk index; Negative values protect against risk.")

        # Create Horizontal Bar Chart for SHAP Impact with generous left margin for y-axis labels
        df_chart = df_exp.copy()
        df_chart["color"] = df_chart["shap_impact"].apply(lambda x: "#EF4444" if x > 0 else "#10B981")
        df_chart["impact_label"] = df_chart["shap_impact"].apply(lambda x: f"+{x*100:.1f}%" if x > 0 else f"{x*100:.1f}%")

        fig = go.Figure(go.Bar(
            x=df_chart["shap_impact"] * 100,
            y=df_chart["feature_label"],
            orientation='h',
            marker=dict(color=df_chart["color"]),
            text=df_chart["impact_label"],
            textposition="auto"
        ))

        fig.update_layout(
            height=460,
            margin=dict(l=240, r=20, t=20, b=30),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(248,250,252,0.5)',
            font=dict(family="Inter", size=13, color="#0F172A"),
            xaxis=dict(title="SHAP Risk Score Impact (Percentage Points)", showgrid=True, gridcolor="#CBD5E1", tickfont=dict(color="#0F172A")),
            yaxis=dict(autorange="reversed", tickfont=dict(color="#0F172A", size=12))
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 🚨 Primary Risk Contributors")
        if not risk_drivers.empty:
            for idx, r in risk_drivers.head(4).iterrows():
                f_label = r["feature_label"]
                val = r["value"]
                impact_pct = int(r["shap_impact"] * 100)
                st.markdown(f"""
                <div style="background: #FEF2F2; border-left: 4px solid #EF4444; padding: 12px; border-radius: 6px; margin-bottom: 10px;">
                    <div style="font-weight: 700; color: #991B1B;">{f_label} (+{impact_pct}%)</div>
                    <div style="font-size: 0.85rem; color: #7F1D1D;">Current metric value: <b>{val:.1f}</b></div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No significant risk-elevating drivers detected.")

        st.markdown("### 🛡️ Protective Factors")
        if not protective.empty:
            for idx, r in protective.head(3).iterrows():
                f_label = r["feature_label"]
                val = r["value"]
                impact_pct = int(r["shap_impact"] * 100)
                st.markdown(f"""
                <div style="background: #ECFDF5; border-left: 4px solid #10B981; padding: 12px; border-radius: 6px; margin-bottom: 10px;">
                    <div style="font-weight: 700; color: #065F46;">{f_label} ({impact_pct}%)</div>
                    <div style="font-size: 0.85rem; color: #047857;">Current metric value: <b>{val:.1f}</b></div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No major protective factors detected.")

    # 3. Advanced Technical SHAP Table Accordion
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    with st.expander("🔬 Advanced Technical SHAP Matrix"):
        st.dataframe(
            df_exp[["feature", "feature_label", "value", "shap_impact"]].rename(columns={
                "feature": "Feature Name",
                "feature_label": "Description",
                "value": "Raw Value",
                "shap_impact": "SHAP Impact Value"
            }),
            use_container_width=True
        )

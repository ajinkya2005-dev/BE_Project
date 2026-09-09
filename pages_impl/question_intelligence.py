import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.models import get_all_subjects, get_question_papers_for_subject, get_questions_for_paper
from ocr.question_paper_ocr import parse_question_paper_file, compute_topic_importance_scores
from utils.helpers import render_alert_box

def render_question_intelligence_page():
    """Render Question Paper Intelligence & Topic Ranking Page."""
    st.markdown('<div class="header-title">Question Paper Intelligence & Topic Importance</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">OCR extraction, historical exam pattern mining, and topic importance ranking</div>', unsafe_allow_html=True)

    # Transparency Disclaimer Banner
    render_alert_box(
        "ℹ️ <b>PROTOTYPE BOUNDARY NOTICE:</b> Topic Importance Scores represent <b>Historical Examination Frequency & Weightage</b> "
        "mined from prior papers (2023–2025). This is strictly an academic prioritization tool and <b>NOT a prediction of future examination questions</b>.",
        severity="info"
    )

    subjects = get_all_subjects()
    if not subjects:
        st.warning("No subjects found in database.")
        return

    subj_dict = {f"{s['subject_code']} - {s['subject_name']}": s["id"] for s in subjects}
    selected_subj_label = st.selectbox("Select Academic Subject for Analysis", list(subj_dict.keys()))
    subject_id = subj_dict[selected_subj_label]

    tab1, tab2, tab3 = st.tabs(["📊 Topic Importance Matrix", "📜 Historical Question Papers", "📤 Upload New Paper (OCR)"])

    with tab1:
        st.markdown("### 🏆 Mined Topic Importance Ranking (0–100)")
        rankings = compute_topic_importance_scores(subject_id)

        df_rank = pd.DataFrame(rankings)
        if not df_rank.empty:
            df_rank_display = df_rank.rename(columns={
                "unit_number": "Unit",
                "topic_name": "Topic Name",
                "frequency": "Exam Frequency",
                "total_marks": "Total Marks Weight",
                "last_appeared": "Last Appeared Year",
                "importance_score": "Importance Score (0-100)"
            })

            col_t, col_c = st.columns([0.55, 0.45])
            with col_t:
                st.dataframe(df_rank_display[["Unit", "Topic Name", "Exam Frequency", "Total Marks Weight", "Last Appeared Year", "Importance Score (0-100)"]], use_container_width=True)

            with col_c:
                st.markdown("#### Importance Score Heatmap")
                fig_h = go.Figure(go.Bar(
                    x=df_rank["importance_score"],
                    y=df_rank["topic_name"],
                    orientation='h',
                    marker=dict(color="#4F46E5"),
                    text=df_rank["importance_score"],
                    textposition="auto"
                ))
                fig_h.update_layout(
                    height=280,
                    margin=dict(l=180, r=20, t=10, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(248,250,252,0.5)',
                    font=dict(family="Inter", size=12, color="#0F172A"),
                    xaxis=dict(title="Importance Score (0-100)", range=[0, 100], showgrid=True, gridcolor="#CBD5E1"),
                    yaxis=dict(autorange="reversed", tickfont=dict(color="#0F172A", size=11, weight="bold"))
                )
                st.plotly_chart(fig_h, use_container_width=True)

    with tab2:
        st.markdown("### 📄 Historical Examination Papers")
        papers = get_question_papers_for_subject(subject_id)

        if papers:
            for p in papers:
                with st.expander(f"📖 {selected_subj_label} — Year {p['year']} ({p['exam_type']}) - Total Marks: {p['total_marks']}"):
                    questions = get_questions_for_paper(p["id"])
                    if questions:
                        for q in questions:
                            t_name = q.get("topic_name") or "General"
                            st.write(f"**{q['question_number']}** ({q['marks']} marks) [Unit {q['unit']} • Topic: *{t_name}*]")
                            st.write(f"> {q['question_text']}")
                    else:
                        st.info("No questions logged for this paper.")
        else:
            st.info("No question papers logged for this subject yet.")

    with tab3:
        st.markdown("### 📤 Upload Question Paper for OCR Extraction")
        uploaded_file = st.file_uploader("Upload Examination Paper (PDF, PNG, JPG, TXT)", type=["pdf", "png", "jpg", "jpeg", "txt"])

        if uploaded_file is not None:
            bytes_data = uploaded_file.read()
            st.success(f"File '{uploaded_file.name}' received ({len(bytes_data)} bytes). Running OCR Extraction pipeline...")

            extracted_questions = parse_question_paper_file(bytes_data, uploaded_file.name)

            st.markdown("#### 🎯 Extracted Questions & Structured Parsing Results:")
            for idx, q in enumerate(extracted_questions, 1):
                st.markdown(f"""
                <div style="background: white; border-left: 4px solid #4F46E5; padding: 12px; border-radius: 6px; margin-bottom: 8px; border: 1px solid #E2E8F0;">
                    <b style="color: #0F172A;">{q['question_number']}</b> ({q['marks']} marks) <br/>
                    <span style="color: #1E293B;">{q['question_text']}</span>
                </div>
                """, unsafe_allow_html=True)

import streamlit as st

def render_methodology_page():
    """Render AI Methodology & Transparency Document."""
    st.markdown('<div class="header-title">AI Methodology & System Architecture</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">Technical description of Machine Learning, SHAP XAI, OCR, RAG, and Adaptive Planning algorithms</div>', unsafe_allow_html=True)

    st.markdown("""
    ### 🎯 1. Dropout Risk Prediction Model
    The core risk model uses supervised binary classification trained on academic indicators (Attendance, CGPA, Backlogs, Assignment Completion, Quiz Scores, LMS Activity, and Score Trends).
    - **Algorithms:** Random Forest Classifier & Logistic Regression.
    - **Optimization Objective:** High Recall and ROC-AUC to minimize false negatives (unidentified at-risk students).
    - **Reproducibility:** Seeded random generator with standard feature scaling.

    ### 🔍 2. Explainable AI (SHAP)
    To avoid "black-box" predictions, EduGuard AI computes feature attribution using **SHAP (SHapley Additive exPlanations)**.
    - Quantifies exact percentage point contribution of each academic feature toward risk elevation or protection.
    - Translates SHAP values into student-friendly natural language narratives.

    ### 📄 3. Question Paper Intelligence (OCR & Topic Ranking)
    - Uses optical character recognition (OCR) and pattern matching to parse raw examination papers into structured question objects.
    - Computes **Topic Importance Scores (0–100)** by combining question frequency, total marks weightage, recency of appearance (2023–2025), and topic repetition.

    ### 📅 4. Adaptive Study Planner Engine
    - Multi-factor study task prioritization combining Student Risk, Subject Risk, Topic Weakness (<55%), and Exam Topic Importance Score.
    - **Closed-Loop Feedback:** As students complete study blocks and achieve higher quiz scores, the adaptive engine recalculates topic weakness and shifts study priority to newly identified weak areas.

    ### 🤖 5. RAG AI Academic Counselor
    - Combines document vector retrieval over academic knowledge bases (syllabus notes, exam strategies, advising FAQs) with local context extraction.
    - Operates **100% offline-first** with deterministic intelligent fallback, and supports optional external LLM API integration.

    ---
    > **⚠️ Prototype Boundary Notice:** EduGuard AI is a research prototype created for academic evaluation. Risk scores and topic importance metrics represent synthetic baseline algorithms for demonstration purposes and are not institutionally certified medical or diagnostic instruments.
    """)

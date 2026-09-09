import streamlit as st
from database.models import get_student_by_id, get_student_by_user_id, get_all_students
from rag.counselor import query_ai_counselor
from utils.helpers import render_alert_box

def render_counselor_view():
    """Render RAG AI Counselor Chat Interface with distinct Student and Faculty modes."""
    user = st.session_state.get("user") or {}
    role = st.session_state.get("role") or "Student"
    profile = st.session_state.get("profile") or {}
    is_faculty_mode = role in ["Faculty", "Admin"]

    # 1. Faculty / Admin Mode Setup
    if is_faculty_mode:
        all_students = get_all_students()
        if all_students:
            stu_dict = {f"{s['student_code']} - {s['full_name']} ({int(s['current_risk_score']*100)}% {s['current_risk_level']} Risk)": s["id"] for s in all_students}
            sel_label = st.selectbox("Select Student to Counsel / Generate Advising Insights", list(stu_dict.keys()), key="fac_counsel_stu_sel")
            student_id = stu_dict[sel_label]
            profile = get_student_by_id(student_id) or profile

        st.markdown('<div class="header-title">EduGuard AI Faculty Advising Counselor</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="header-subtitle">Pedagogical advising assistant generating student-specific intervention strategies for {profile.get("full_name", "Student")}</div>', unsafe_allow_html=True)

        render_alert_box(
            f"👨‍🏫 <b>FACULTY ADVISING MODE ACTIVE:</b> Generating tailored intervention strategies and pedagogical advising guidance for <b>{profile.get('full_name', 'Student')}</b> ({profile.get('student_code', 'STU101')}).",
            severity="info"
        )
    else:
        # 2. Student Mode Setup
        if not profile:
            profile = get_student_by_user_id(user.get("id", 1)) or {}

        student_id = profile.get("id", 1)
        if "override_student_id" in st.session_state:
            student_id = st.session_state["override_student_id"]
            profile = get_student_by_id(student_id) or profile

        st.markdown('<div class="header-title">EduGuard AI Personal Study Counselor</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="header-subtitle">Interactive RAG AI study advisor tailored for {profile.get("full_name", "Student")}</div>', unsafe_allow_html=True)

        render_alert_box(
            "🤖 <b>PERSONAL STUDY ADVISOR ONLINE:</b> Analyzing your study plan, unit quiz scores, SHAP risk drivers, and syllabus knowledge base to formulate context-aware study advice.",
            severity="info"
        )

    name = profile.get("full_name", "Student")
    st_id = profile.get("id", 1)
    risk_pct = int(float(profile.get("current_risk_score", 0.25)) * 100)
    risk_lvl = profile.get("current_risk_level", "LOW")

    # Chat history unique key per role & student
    chat_key = f"chat_msg_{'fac' if is_faculty_mode else 'stu'}_{st_id}"
    if chat_key not in st.session_state:
        if is_faculty_mode:
            init_msg = f"Welcome Professor! You are analyzing **{name}** ({st_id} • {risk_pct}% {risk_lvl} Risk). How can I assist with pedagogical advising or intervention strategy for this student today?"
        else:
            init_msg = f"Hello {name}! I am your EduGuard AI Personal Study Advisor. How can I assist with your daily study strategy or risk reduction today?"
        
        st.session_state[chat_key] = [{"role": "assistant", "content": init_msg}]

    # Role-Specific Quick Prompts
    st.caption("💡 Quick Prompts:")
    quick_query = None

    if is_faculty_mode:
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"🎯 Recommend Intervention Strategy for {name}", use_container_width=True, key="btn_f1"):
                quick_query = f"What intervention strategy is recommended for {name}?"
            if st.button(f"📊 Summarize Top Risk Factors for {name}", use_container_width=True, key="btn_f2"):
                quick_query = f"Summarize the primary risk factors for {name}."
        with c2:
            if st.button(f"📚 Review Subject Performance for {name}", use_container_width=True, key="btn_f3"):
                quick_query = f"How is {name} performing across high-risk subjects?"
            if st.button(f"💬 1-on-1 Mentoring Session Guidance for {name}", use_container_width=True, key="btn_f4"):
                quick_query = f"How should I structure the 1-on-1 counseling session for {name}?"
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("❓ What should I study first today?", use_container_width=True, key="btn_s1"):
                quick_query = "What should I study first?"
            if st.button("📊 Why is my risk score elevated?", use_container_width=True, key="btn_s2"):
                quick_query = "Why is my risk elevated?"
        with c2:
            if st.button("🗄️ How to improve DBMS score?", use_container_width=True, key="btn_s3"):
                quick_query = "How can I improve my DBMS performance?"
            if st.button("🏆 Important exam topics?", use_container_width=True, key="btn_s4"):
                quick_query = "What are the important DBMS topics?"
        with c3:
            if st.button("🔒 Why study deadlocks?", use_container_width=True, key="btn_s5"):
                quick_query = "Why should I study deadlocks?"

    # Display Chat History with clean emoji avatars (no Material Symbol text bugs)
    for msg in st.session_state[chat_key]:
        avatar_icon = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar_icon):
            st.markdown(msg["content"])

    # Chat Input Processing
    placeholder_text = f"Ask advising question about {name}..." if is_faculty_mode else "Ask EduGuard AI Study Counselor..."
    user_input = st.chat_input(placeholder_text)
    active_prompt = user_input or quick_query

    if active_prompt:
        # User message
        st.session_state[chat_key].append({"role": "user", "content": active_prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(active_prompt)

        # Assistant response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analyzing profile & retrieving knowledge context..."):
                response_data = query_ai_counselor(active_prompt, profile, is_faculty=is_faculty_mode)
                ans = response_data["answer"]
                st.markdown(ans)
                st.session_state[chat_key].append({"role": "assistant", "content": ans})

        if quick_query:
            st.rerun()

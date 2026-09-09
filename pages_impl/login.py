import streamlit as st
from auth.authentication import login_user, register_student, register_faculty
from config import DEMO_CREDENTIALS, COLOR_PALETTE

def render_login_page():
    """Render application login and registration landing page."""
    st.markdown('<div class="header-title">EduGuard AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">Explainable Academic Intelligence & Early Intervention Platform</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.1, 0.9])

    with col1:
        st.markdown("""
        <div style="background: white; padding: 24px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px;">
            <h3 style="color: #4F46E5; margin-top: 0;">Predict. Explain. Intervene. Adapt.</h3>
            <p style="color: #475569; font-size: 0.95rem; line-height: 1.6;">
                EduGuard AI empowers institutions to identify student academic risk early through <b>Explainable Machine Learning (SHAP)</b>, 
                generate <b>adaptive personalized study plans</b> based on historical examination intelligence (OCR), and monitor 
                the complete <b>closed-loop intervention workflow</b>.
            </p>
            <div style="display: flex; gap: 12px; margin-top: 16px;">
                <span style="background: #EEF2FF; color: #4F46E5; padding: 6px 12px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">🎯 Risk Prediction</span>
                <span style="background: #F3E8FF; color: #7C3AED; padding: 6px 12px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">🔍 SHAP XAI</span>
                <span style="background: #ECFDF5; color: #059669; padding: 6px 12px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">📅 Adaptive Planner</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### ⚡ Quick Demo Accounts")
        st.caption("Click any button below to instantly populate demo credentials and log in:")

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🎓 Student Demo", use_container_width=True):
                success, user_data, msg = login_user(
                    DEMO_CREDENTIALS["Student"]["email"],
                    DEMO_CREDENTIALS["Student"]["pass"],
                    "Student"
                )
                if success:
                    st.rerun()

        with c2:
            if st.button("👨‍🏫 Faculty Demo", use_container_width=True):
                success, user_data, msg = login_user(
                    DEMO_CREDENTIALS["Faculty"]["email"],
                    DEMO_CREDENTIALS["Faculty"]["pass"],
                    "Faculty"
                )
                if success:
                    st.rerun()

        with c3:
            if st.button("⚙️ Admin Demo", use_container_width=True):
                success, user_data, msg = login_user(
                    DEMO_CREDENTIALS["Admin"]["email"],
                    DEMO_CREDENTIALS["Admin"]["pass"],
                    "Admin"
                )
                if success:
                    st.rerun()

    with col2:
        tab_login, tab_reg_student, tab_reg_faculty = st.tabs(["🔒 Secure Login", "📝 Student Register", "👩‍🏫 Faculty Register"])

        with tab_login:
            st.subheader("Account Sign In")
            role = st.selectbox("Select Account Role", ["Student", "Faculty", "Admin"], key="login_role")
            email = st.text_input("Email Address", value=DEMO_CREDENTIALS[role]["email"])
            password = st.text_input("Password", type="password", value=DEMO_CREDENTIALS[role]["pass"])

            if st.button("Sign In to EduGuard AI", use_container_width=True):
                success, user_data, msg = login_user(email, password, role)
                if success:
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(msg)

        with tab_reg_student:
            st.subheader("Student Registration")
            s_name = st.text_input("Full Name", key="reg_s_name")
            s_email = st.text_input("Email", key="reg_s_email")
            s_pass = st.text_input("Password", type="password", key="reg_s_pass")
            s_code = st.text_input("Student ID (e.g. STU199)", key="reg_s_code")
            s_dept = st.selectbox("Department", ["Computer Engineering", "Information Technology", "Data Science"], key="reg_s_dept")
            s_sem = st.number_input("Semester", min_value=1, max_value=8, value=5, key="reg_s_sem")

            if st.button("Register Student Account", use_container_width=True):
                if s_name and s_email and s_pass and s_code:
                    success, msg = register_student(s_email, s_pass, s_name, s_code, s_dept, int(s_sem), "A", 2023)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill in all required fields.")

        with tab_reg_faculty:
            st.subheader("Faculty Registration")
            f_name = st.text_input("Full Name", key="reg_f_name")
            f_email = st.text_input("Email", key="reg_f_email")
            f_pass = st.text_input("Password", type="password", key="reg_f_pass")
            f_code = st.text_input("Faculty ID (e.g. FAC199)", key="reg_f_code")
            f_dept = st.selectbox("Department", ["Computer Engineering", "Information Technology"], key="reg_f_dept")
            f_desig = st.selectbox("Designation", ["Assistant Professor", "Associate Professor", "Professor"], key="reg_f_desig")

            if st.button("Register Faculty Account", use_container_width=True):
                if f_name and f_email and f_pass and f_code:
                    success, msg = register_faculty(f_email, f_pass, f_name, f_code, f_dept, f_desig)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill in all required fields.")

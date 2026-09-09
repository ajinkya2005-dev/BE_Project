import os
import sys
import streamlit as st

# Ensure root directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import APP_NAME, APP_SUBTITLE
from database.seed import seed_database
from ml.risk_model import load_or_train_model
from auth.authentication import logout_user
from utils.styling import apply_custom_theme

# UI Page Implementation Imports
from pages_impl.login import render_login_page
from pages_impl.student_dashboard import render_student_dashboard
from pages_impl.faculty_dashboard import render_faculty_dashboard
from pages_impl.risk_analysis import render_risk_analysis_page
from pages_impl.study_planner_view import render_study_planner_view
from pages_impl.question_intelligence import render_question_intelligence_page
from pages_impl.counselor_view import render_counselor_view
from pages_impl.interventions_view import render_interventions_view
from pages_impl.closed_loop_demo import render_closed_loop_demo
from pages_impl.admin_dashboard import render_admin_dashboard
from pages_impl.methodology import render_methodology_page

def initialize_application():
    """Ensure database is created and seeded, and ML model is initialized."""
    seed_database(force=False)
    load_or_train_model()

def main():
    """Streamlit Application Entrypoint."""
    st.set_page_config(
        page_title=f"{APP_NAME} — {APP_SUBTITLE}",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize theme and backend state
    initialize_application()
    apply_custom_theme()

    # Session State Auth Tracking
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        render_login_page()
        return

    # User Role & Profile
    user = st.session_state.get("user") or {}
    role = st.session_state.get("role") or "Student"
    profile = st.session_state.get("profile") or {}
    user_email = user.get("email", "")

    # Sidebar Header & Navigation
    st.sidebar.markdown(f"## 🎓 {APP_NAME}")
    st.sidebar.caption(f"Role: **{role}** | User: {user_email}")
    st.sidebar.markdown("---")

    # Role-based Navigation Menus
    if role == "Student":
        nav_options = [
            "📊 Dashboard Overview",
            "🔍 Why am I at Risk? (XAI)",
            "📅 Adaptive Study Planner",
            "📄 Question Intelligence",
            "🤖 AI Academic Counselor",
            "📋 My Interventions",
            "🔄 Closed-Loop AI Demo",
            "🔬 AI Methodology"
        ]
    elif role == "Faculty":
        nav_options = [
            "👨‍🏫 Faculty Cohort Dashboard",
            "🔍 Cohort SHAP Risk Breakdown",
            "📋 Remedial Interventions",
            "📄 Question Intelligence",
            "💡 Faculty Advising Counselor",
            "🔄 Closed-Loop AI Demo",
            "🔬 AI Methodology"
        ]
    else:  # Admin
        nav_options = [
            "⚙️ Admin System Overview",
            "👨‍🏫 Institutional Risk Monitoring",
            "📄 Question Intelligence",
            "🔄 Closed-Loop AI Demo",
            "🔬 AI Methodology"
        ]

    selected_nav = st.sidebar.radio("Navigation Menu", nav_options)

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Sign Out / Logout", use_container_width=True):
        logout_user()
        st.rerun()

    # Page Routing
    if selected_nav in ["📊 Dashboard Overview"]:
        render_student_dashboard()
    elif selected_nav in ["👨‍🏫 Faculty Cohort Dashboard", "👨‍🏫 Institutional Risk Monitoring"]:
        render_faculty_dashboard()
    elif selected_nav in ["🔍 Why am I at Risk? (XAI)", "🔍 Cohort SHAP Risk Breakdown"]:
        render_risk_analysis_page()
    elif selected_nav in ["📅 Adaptive Study Planner"]:
        render_study_planner_view()
    elif selected_nav in ["📄 Question Intelligence"]:
        render_question_intelligence_page()
    elif selected_nav in ["🤖 AI Academic Counselor", "💡 Faculty Advising Counselor"]:
        render_counselor_view()
    elif selected_nav in ["📋 My Interventions", "📋 Remedial Interventions"]:
        render_interventions_view()
    elif selected_nav in ["🔄 Closed-Loop AI Demo"]:
        render_closed_loop_demo()
    elif selected_nav in ["⚙️ Admin System Overview"]:
        render_admin_dashboard()
    elif selected_nav in ["🔬 AI Methodology"]:
        render_methodology_page()

if __name__ == "__main__":
    # Check if executed via standard python CLI `python main.py` directly
    if not st.runtime.exists():
        import subprocess
        print(f"Launching Streamlit application: streamlit run main.py ...")
        cmd = [sys.executable, "-m", "streamlit", "run", __file__]
        subprocess.run(cmd)
    else:
        main()

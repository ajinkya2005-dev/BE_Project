import os

# Application Metadata
APP_NAME = "EduGuard AI"
APP_SUBTITLE = "Explainable Academic Intelligence & Early Intervention Platform"
VERSION = "1.0.0"

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "eduguard.db")
MODEL_PATH = os.path.join(BASE_DIR, "ml", "model.pkl")

# Ensure required directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "ml"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)

# Risk Category Thresholds (Prototype boundaries)
RISK_THRESHOLDS = {
    "LOW": (0.0, 0.35),
    "MEDIUM": (0.35, 0.65),
    "HIGH": (0.65, 1.0)
}

# Branding & UI Colors
COLOR_PALETTE = {
    "primary": "#4F46E5",
    "primary_hover": "#4338CA",
    "secondary": "#7C3AED",
    "accent": "#06B6D4",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "bg_light": "#F8FAFC",
    "text_dark": "#0F172A",
    "card_bg": "#FFFFFF",
    "border": "#E2E8F0"
}

# Risk Level Colors for Visual Elements
RISK_COLORS = {
    "LOW": "#10B981",
    "MEDIUM": "#F59E0B",
    "HIGH": "#EF4444"
}

# Demo Credentials
DEMO_CREDENTIALS = {
    "Student": {"email": "student1@eduguard.ai", "pass": "student123"},
    "Faculty": {"email": "faculty@eduguard.ai", "pass": "faculty123"},
    "Admin": {"email": "admin@eduguard.ai", "pass": "admin123"}
}

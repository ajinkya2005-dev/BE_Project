# EduGuard AI — Explainable Student Dropout Risk Prediction, Personalized Intervention & Adaptive Study Planning

**EduGuard AI** is a working prototype platform designed for AIML academic demonstration. It integrates explainable dropout risk prediction, SHAP feature attribution, historical examination paper mining (OCR), adaptive personalized study planning, and closed-loop intervention tracking into a single unified EdTech software application.

---

## 🌟 Key Features

1. **Explainable Dropout Risk Prediction:** Supervised machine learning (Random Forest & Logistic Regression) evaluating academic indicators (attendance, CGPA, backlogs, trends, engagement).
2. **SHAP Feature Attribution (XAI):** Transparent breakdown of top risk drivers (+%) and protective factors (-%) with jargon-free natural language explanations.
3. **Subject & Topic Weakness Analysis:** Identifies topic mastery levels (*Weak*, *Moderate*, *Strong*) derived from assessment quiz performance.
4. **Question Paper Intelligence (OCR):** Extracts examination questions from uploaded papers and computes **Topic Importance Scores (0–100)** based on frequency, recency, and marks weightage.
5. **Adaptive Study Planner:** Dynamically prioritizes study tasks combining risk score, topic weakness, and exam importance. Automatically adapts priorities when students record score improvements!
6. **RAG AI Academic Counselor:** Local RAG intelligent assistant providing contextual academic advice based on student risk state and syllabus knowledge base. Works 100% offline without external API keys.
7. **Closed-Loop Intervention Tracking:** Enables faculty to initiate remedial intervention plans and monitor before/after risk score reduction.
8. **10-Step Interactive Closed-Loop Demo:** Visual step-by-step demonstration of the complete research lifecycle.

---

## 🚀 One-Command Quickstart Guide

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13

### Step 1: Clone Repository & Install Dependencies
```bash
git clone https://github.com/your-username/EduGuard-AI.git
cd EduGuard-AI
pip install -r requirements.txt
```

### Step 2: Run Application
You can launch the application with either command:

**Option A (Streamlit CLI):**
```bash
streamlit run main.py
```

**Option B (Python convenience launcher):**
```bash
python main.py
```

> **Note:** The SQLite database (`eduguard.db`) and ML model (`ml/model.pkl`) will be **automatically created, populated with seed data, and trained** on first launch. No manual setup required!

---

## 🔐 Pre-Seeded Demo Credentials

Click the **Quick Demo Buttons** on the login page or enter these credentials:

| Role | Email Address | Password |
| :--- | :--- | :--- |
| **Student** | `student1@eduguard.ai` | `student123` |
| **Faculty** | `faculty@eduguard.ai` | `faculty123` |
| **Admin** | `admin@eduguard.ai` | `admin123` |

---

## 🏗️ Project Architecture & Structure

```
EduGuard-AI/
├── main.py                          # Application entry point & launcher
├── config.py                        # Central settings, palette & risk thresholds
├── requirements.txt                 # Project dependencies
├── README.md                        # Documentation
├── .gitignore                       # Git ignore rules
│
├── database/                        # Persistence & Seed Layer
│   ├── database.py                  # SQLite schema (14 tables)
│   ├── models.py                    # Data access objects (DAOs)
│   └── seed.py                      # Realistic student profile generator
│
├── auth/                            # Authentication & Session
│   └── authentication.py            # Password hashing (SHA-256) & login validation
│
├── ml/                              # Machine Learning Pipeline
│   ├── risk_model.py                # Dropout risk classifier & persistence
│   ├── feature_engineering.py       # Student feature extraction
│   └── evaluator.py                 # Classification metrics
│
├── xai/                             # Explainable AI
│   └── explainer.py                 # SHAP values & natural language generator
│
├── analytics/                       # Academic Analytics
│   ├── subject_risk.py              # Subject-level risk calculator
│   ├── topic_analysis.py            # Topic weakness evaluator
│   └── longitudinal.py              # Time-series trend analytics
│
├── ocr/                             # Question Paper Intelligence
│   └── question_paper_ocr.py        # OCR text parsing & Topic Importance Scoring
│
├── rag/                             # RAG Counselor Engine
│   ├── embeddings.py                # Knowledge retrieval search
│   ├── retriever.py                 # Knowledge document index
│   └── counselor.py                 # Intelligent local RAG response engine
│
├── planner/                         # Adaptive Study Planner
│   └── study_planner.py             # Multi-factor priority schedule generator
│
├── intervention/                    # Intervention Workflow
│   └── intervention_tracker.py      # Pre/post intervention efficacy tracker
│
├── pages_impl/                      # Streamlit UI Views
│   ├── login.py                     # Sign-in & registration
│   ├── student_dashboard.py         # Personalized student risk dashboard
│   ├── faculty_dashboard.py         # Cohort risk monitoring & student detail drill-down
│   ├── risk_analysis.py             # SHAP XAI breakdown
│   ├── study_planner_view.py        # Adaptive study planner view
│   ├── question_intelligence.py     # OCR paper upload & topic importance ranking
│   ├── counselor_view.py            # AI counselor chat UI
│   ├── interventions_view.py        # Intervention tracking
│   ├── closed_loop_demo.py          # 10-step interactive workflow demo
│   ├── admin_dashboard.py           # Admin overview & re-seed controls
│   └── methodology.py               # AI transparency & methodology document
│
└── utils/                           # UI Styling & Helpers
    ├── styling.py                   # Custom CSS theme, badges & Plotly visuals
    └── helpers.py                   # CSV export & formatting helpers
```

---

## 🔬 AI & ML Methodology

1. **Predict:** Supervised Random Forest Classifier trained on student attendance, CGPA, backlogs, engagement score, LMS activity, and historical trends.
2. **Explain:** SHAP (SHapley Additive exPlanations) isolates feature contributions to eliminate black-box opacity.
3. **Mine:** Pattern mining computes **Topic Importance Scores (0–100)** from prior examination papers.
4. **Adapt:** Real-time feedback loop recalculates risk scores and shifts study task priorities whenever student marks or attendance improve.

---

## ⚠️ Prototype Boundaries & Disclaimer

This software is an academic demonstration prototype:
- Risk scores and topic importance metrics represent synthetic baseline algorithms for evaluation purposes.
- Historical topic importance scores reflect past exam frequency and do not guarantee future exam questions.
- All pre-seeded student records represent synthetic demonstration data.

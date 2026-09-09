import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from config import COLOR_PALETTE, RISK_COLORS

def apply_custom_theme():
    """Inject custom modern EdTech CSS theme with 100% crisp input, selectbox, button, and font visibility."""
    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="st-"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #0F172A;
        }}

        .stApp {{
            background-color: #F8FAFC !important;
            color: #0F172A !important;
        }}

        /* Force high contrast text on standard Streamlit elements */
        div[data-testid="stMainBlockContainer"] p,
        div[data-testid="stMainBlockContainer"] span,
        div[data-testid="stMainBlockContainer"] label,
        div[data-testid="stMainBlockContainer"] h1,
        div[data-testid="stMainBlockContainer"] h2,
        div[data-testid="stMainBlockContainer"] h3,
        div[data-testid="stMainBlockContainer"] h4,
        div[data-testid="stMainBlockContainer"] h5,
        div[data-testid="stMainBlockContainer"] h6,
        div[data-testid="stWidgetLabel"] p,
        div[data-testid="stWidgetLabel"] span {{
            color: #0F172A !important;
            font-weight: 600;
        }}

        .stCaption, small, [data-testid="stCaptionContainer"] p {{
            color: #334155 !important;
            font-weight: 600 !important;
        }}

        /* Main Container Cards */
        .eduguard-card {{
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
            color: #0F172A;
        }}

        /* Metric Banner Cards */
        .metric-card {{
            background: #FFFFFF;
            border-radius: 12px;
            padding: 16px 18px;
            border-left: 4px solid {COLOR_PALETTE['primary']};
            border-top: 1px solid #E2E8F0;
            border-right: 1px solid #E2E8F0;
            border-bottom: 1px solid #E2E8F0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
            word-break: break-word;
        }}

        .metric-card-high {{
            border-left: 5px solid {RISK_COLORS['HIGH']};
            background: #FEF2F2;
        }}
        .metric-card-medium {{
            border-left: 5px solid {RISK_COLORS['MEDIUM']};
            background: #FFFBEB;
        }}
        .metric-card-low {{
            border-left: 5px solid {RISK_COLORS['LOW']};
            background: #ECFDF5;
        }}

        .metric-label {{
            font-size: 0.82rem;
            font-weight: 700;
            color: #334155;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }}

        .metric-value {{
            font-size: 1.75rem;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.2;
        }}

        /* Status Pills */
        .status-pill {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .pill-high {{ background-color: #FEE2E2; color: #991B1B; }}
        .pill-medium {{ background-color: #FEF3C7; color: #92400E; }}
        .pill-low {{ background-color: #D1FAE5; color: #065F46; }}

        /* Primary Header Accent */
        .header-title {{
            font-size: 2.1rem;
            font-weight: 800;
            color: #4F46E5;
            background: linear-gradient(135deg, {COLOR_PALETTE['primary']} 0%, {COLOR_PALETTE['secondary']} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1.3;
            margin-bottom: 4px;
        }}
        .header-subtitle {{
            font-size: 1.02rem;
            color: #334155;
            font-weight: 500;
            margin-bottom: 24px;
        }}

        /* ALL INPUT FIELDS & SELECTBOXES: WHITE BACKGROUND + DARK VISIBLE TEXT */
        div[data-baseweb="input"],
        div[data-baseweb="select"],
        div[data-baseweb="base-input"],
        div[data-testid="stTextInput"] input,
        div[data-testid="stSelectbox"] div[role="combobox"],
        div[data-testid="stTextArea"] textarea,
        input, textarea, select {{
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }}

        /* Selected value text inside selectbox box */
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div,
        div[data-testid="stSelectbox"] span,
        div[data-testid="stSelectbox"] p {{
            color: #0F172A !important;
            font-weight: 700 !important;
        }}

        /* Dropdown popover list item choices when menu opens */
        div[data-baseweb="popover"] *,
        div[role="listbox"] *,
        div[role="option"] *,
        div[data-baseweb="menu"] * {{
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            font-weight: 600 !important;
        }}

        /* Custom Buttons — Prevent label truncation */
        .stButton > button {{
            background-color: {COLOR_PALETTE['primary']} !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: 700 !important;
            padding: 8px 14px !important;
            white-space: normal !important;
            word-wrap: break-word !important;
            height: auto !important;
            min-height: 42px !important;
            transition: all 0.2s ease;
        }}
        .stButton > button:hover {{
            background-color: {COLOR_PALETTE['primary_hover']} !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        }}
        .stButton > button p, .stButton > button span {{
            color: #FFFFFF !important;
            font-weight: 700 !important;
            white-space: normal !important;
            word-wrap: break-word !important;
        }}

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {{
            background-color: #1E1B4B !important;
        }}
        section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] div[role="radiogroup"] label span {{
            color: #FFFFFF !important;
            font-weight: 600;
        }}
        div[data-testid="stSidebarNav"] {{
            padding-top: 10px;
        }}

        /* Fix Streamlit sidebar collapse arrow icon text glitch (hide literal 'keyboard_double' text) */
        button[aria-label*="sidebar"] span,
        button[data-testid="stSidebarCollapseButton"] span,
        div[data-testid="stSidebarUserContent"] > div:first-child button span {{
            font-size: 0px !important;
        }}

        /* Streamlit Tabs */
        button[data-baseweb="tab"] p, button[data-baseweb="tab"] span {{
            font-weight: 700 !important;
            color: #1E293B !important;
        }}

        /* Fix Streamlit Expander Overlapping Header Icon */
        div[data-testid="stExpander"] details summary {{
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
            padding: 10px 14px !important;
        }}
        div[data-testid="stExpander"] details summary span {{
            color: #0F172A !important;
            font-weight: 700 !important;
        }}

        /* Streamlit Metrics */
        div[data-testid="stMetricValue"] {{
            color: #0F172A !important;
            font-weight: 800 !important;
        }}
        div[data-testid="stMetricLabel"] p {{
            color: #334155 !important;
            font-weight: 700 !important;
        }}

        /* Alerts & Callouts */
        .alert-box {{
            padding: 14px 18px;
            border-radius: 8px;
            font-size: 0.95rem;
            margin-bottom: 16px;
        }}
        .alert-info {{ background-color: #EFF6FF; border-left: 4px solid #3B82F6; color: #1E40AF; }}
        .alert-warning {{ background-color: #FFFBEB; border-left: 4px solid #F59E0B; color: #92400E; }}
        .alert-critical {{ background-color: #FEF2F2; border-left: 4px solid #EF4444; color: #991B1B; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_metric_card(label: str, value: str, subtext: str = "", risk_level: str = "NORMAL"):
    """Render styled KPI card."""
    card_class = "metric-card"
    if risk_level == "HIGH":
        card_class += " metric-card-high"
    elif risk_level == "MEDIUM":
        card_class += " metric-card-medium"
    elif risk_level == "LOW":
        card_class += " metric-card-low"

    sub_html = f"<div style='font-size: 0.8rem; color: #334155; margin-top: 4px; font-weight: 600;'>{subtext}</div>" if subtext else ""

    html = f"""
    <div class="{card_class}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {sub_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_status_pill(level: str) -> str:
    """Return HTML string for status pill badge."""
    lvl_upper = level.upper()
    pill_cls = "pill-low"
    if lvl_upper == "HIGH":
        pill_cls = "pill-high"
    elif lvl_upper == "MEDIUM":
        pill_cls = "pill-medium"

    return f'<span class="status-pill {pill_cls}">{lvl_upper}</span>'

def create_risk_gauge_chart(risk_score: float) -> go.Figure:
    """Create interactive Plotly radial gauge chart for student risk score."""
    risk_pct = int(risk_score * 100)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_pct,
        number={'suffix': "%", 'font': {'size': 42, 'color': "#0F172A", 'family': "Inter"}},
        title={'text': "Dropout Risk Index", 'font': {'size': 16, 'color': "#0F172A", 'family': "Inter"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#CBD5E1"},
            'bar': {'color': RISK_COLORS["HIGH"] if risk_pct >= 65 else (RISK_COLORS["MEDIUM"] if risk_pct >= 35 else RISK_COLORS["LOW"])},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#E2E8F0",
            'steps': [
                {'range': [0, 35], 'color': "#ECFDF5"},
                {'range': [35, 65], 'color': "#FFFBEB"},
                {'range': [65, 100], 'color': "#FEF2F2"}
            ],
            'threshold': {
                'line': {'color': "#991B1B", 'width': 4},
                'thickness': 0.75,
                'value': 65
            }
        }
    ))

    fig.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': "Inter", 'color': "#0F172A"}
    )
    return fig

def create_trend_line_chart(df, x_col: str, y_col: str, title: str, color: str = "#4F46E5") -> go.Figure:
    """Create polished Plotly line chart for trends."""
    fig = px.line(df, x=x_col, y=y_col, markers=True, title=title)
    fig.update_traces(line_color=color, line_width=3, marker_size=8)
    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(248,250,252,0.5)',
        font={'family': "Inter", 'color': "#0F172A"},
        xaxis=dict(showgrid=True, gridcolor="#CBD5E1", title="Date / Period", tickfont=dict(color="#0F172A")),
        yaxis=dict(showgrid=True, gridcolor="#CBD5E1", title=title, tickfont=dict(color="#0F172A"))
    )
    return fig

import pandas as pd
import streamlit as st
from typing import List, Dict, Any

def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Convert pandas DataFrame to CSV bytes for download button."""
    return df.to_csv(index=False).encode('utf-8')

def format_percentage(val: float) -> str:
    """Format float to percentage string."""
    return f"{int(round(val * 100))}%" if val <= 1.0 else f"{int(round(val))}%"

def render_alert_box(text: str, severity: str = "info"):
    """Render styled notification alert box."""
    css_cls = "alert-info"
    if severity == "warning":
        css_cls = "alert-warning"
    elif severity == "critical":
        css_cls = "alert-critical"

    st.markdown(f'<div class="alert-box {css_cls}">{text}</div>', unsafe_allow_html=True)

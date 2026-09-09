import pandas as pd
from typing import List, Dict, Any
from database.models import get_risk_history

def get_longitudinal_trends(student_id: int) -> pd.DataFrame:
    """
    Retrieve historical time-series data for a student (risk, attendance, engagement, CGPA).
    Returns pandas DataFrame sorted by date with safe timestamp parsing.
    """
    history = get_risk_history(student_id)
    if not history:
        return pd.DataFrame()

    df = pd.DataFrame(history)
    # Use format="mixed" to handle both ISO dates (2025-09-01) and SQLite timestamps (2025-12-01 18:51:22)
    df["calculated_at"] = pd.to_datetime(df["calculated_at"], format="mixed", errors="coerce").dt.strftime("%Y-%m-%d")
    df["risk_pct"] = (df["risk_score"] * 100).round(1)
    return df.sort_values("calculated_at", ascending=True)

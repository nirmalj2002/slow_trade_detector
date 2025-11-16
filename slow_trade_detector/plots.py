# plots.py
"""
Advanced visualization utilities for slow-trade analysis.

Includes:
 - CPU vs Calls scatter with regression, sigma bands
 - CPU per Call plot
 - CPU vs Stress Type (categorical jitter)
 - Anomaly highlighting and annotations
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


# ───────────────────────────────────────────────────────────────
# Utility: safe date + weekday
# ───────────────────────────────────────────────────────────────

def _ensure_date(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure df has 'date' and 'day_of_week' columns."""
    df = df.copy()
    if "date" not in df.columns:
        df["date"] = pd.to_datetime(df.get("eodDate", pd.NaT))
    df["day_of_week"] = df["date"].dt.day_name()
    return df


# ───────────────────────────────────────────────────────────────
# 1. CPU vs Calls (main diagnostic scatter)
# ───────────────────────────────────────────────────────────────

def plot_cpu_vs_calls_enhanced(df: pd.DataFrame, anomaly_col: str = "slow_trade"):
    """
    Scatter: Number of Calls vs CPU Time
    - Regression line
    - ±2σ and ±3σ bands
    - Friday colored differently
    - Anomaly points highlighted
    """
    df = _ensure_date(df)

    # Friday vs others
    friday = df[df["day_of_week"] == "Friday"]
    other  = df[df["day_of_week"] != "Friday"]

    plt.figure(figsize=(12, 8))

    # Plot normal days
    if not other.empty:
        plt.scatter(other["num_calls"], other["cpu_time"],
                    c="blue", alpha=0.6, label="Mon–Thu")

    # Plot Fridays
    if not friday.empty:
        plt.scatter(friday["num_calls"], friday["cpu_time"],
                    c="orange", alpha=0.7, label="Friday")

    # Plot anomalies
    anomalies = df[df.get(anomaly_col, False) == True]
    if not anomalies.empty:
        plt.scatter(anomalies["num_calls"], anomalies["cpu_time"],
                    c="red", s=90, edgecolors="black", label="Anomaly")

        # Labels
        for _, row in anomalies.iterrows():
            label = row.get("secId", row.get("trade_id", ""))
            plt.annotate(str(label),
                         (row["num_calls"], row["cpu_time"]),
                         textcoords="offset points", xytext=(5, 5))

    # ───────────────────────────────────────────────────────────────
    # Regression + sigma bands
    # ───────────────────────────────────────────────────────────────
    good = df.dropna(subset=["num_calls", "cpu_time"])
    if len(good) > 1:
        X = good["num_calls"].values.reshape(-1, 1)
        y = good["cpu_time"].values.reshape(-1, 1)

        reg = LinearRegression().fit(X, y)
        preds = reg.predict(X).flatten()
        sigma = (good["cpu_time"] - preds).std()

        order = np.argsort(good["num_calls"].values)
        xs = good["num_calls"].values[order]
        ys = preds[order]

        # Trendline
        plt.plot(xs, ys, color="black", linewidth=2, label="Trendline")

        # Sigma bands
        plt.fill_between(xs, ys - 2*sigma, ys + 2*sigma,
                         color="gray", alpha=0.2, label="±2σ")
        plt.fill_between(xs, ys - 3*sigma, ys + 3*sigma,
                         color="gray", alpha=0.1, label="±3σ")

    plt.xlabel("Number of Calls")
    plt.ylabel("CPU Time (sec)")
    plt.title("CPU Time vs Number of Calls (Enhanced Diagnostic View)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


# ───────────────────────────────────────────────────────────────
# 2. CPU per Call
# ───────────────────────────────────────────────────────────────

def plot_cpu_per_call_enhanced(df: pd.DataFrame, anomaly_col: str = "slow_trade"):
    """
    Scatter: CPU per Call vs Number of Calls
    - Highlights anomalies
    - Useful when calls have high variance
    """
    df = df.copy()
    df["cpu_per_call"] = df["cpu_time"] / df["num_calls"].replace(0, np.nan)

    plt.figure(figsize=(12, 8))

    normal = df[df.get(anomaly_col, False) == False]
    anomalies = df[df.get(anomaly_col, False) == True]

    if not normal.empty:
        plt.scatter(normal["num_calls"], normal["cpu_per_call"],
                    c="blue", alpha=0.6, label="Normal")

    if not anomalies.empty:
        plt.scatter(anomalies["num_calls"], anomalies["cpu_per_call"],
                    c="red", s=90, edgecolors="black", label="Anomaly")

        for _, row in anomalies.iterrows():
            label = row.get("secId", "")
            plt.annotate(str(label),
                         (row["num_calls"], row["cpu_per_call"]),
                         textcoords="offset points", xytext=(5, 5))

    plt.xlabel("Number of Calls")
    plt.ylabel("CPU per Call (sec)")
    plt.title("CPU per Call vs Number of Calls")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


# ───────────────────────────────────────────────────────────────
# 3. CPU vs Stress Type (categorical jitter plot)
# ───────────────────────────────────────────────────────────────

def plot_cpu_vs_stress_enhanced(df: pd.DataFrame, anomaly_col: str = "slow_trade"):
    """
    Scatter: Stress Type (phase) vs CPU Time
    - Jittered x-axis for better visibility
    - Highlights anomalies
    """
    df = df.copy()

    # Convert phase to categorical codes
    df["phase_cat"] = df["phase"].astype("category")
    codes = df["phase_cat"].cat.codes

    # Add jitter for readability
    jitter = np.random.normal(0, 0.05, size=len(df))
    xvals = codes + jitter

    plt.figure(figsize=(14, 6))

    normal = df[df.get(anomaly_col, False) == False]
    anomalies = df[df.get(anomaly_col, False) == True]

    # Normal points
    if not normal.empty:
        plt.scatter(
            xvals[normal.index], normal["cpu_time"],
            c="blue", alpha=0.6, label="Normal"
        )

    # Anomalies
    if not anomalies.empty:
        plt.scatter(
            xvals[anomalies.index], anomalies["cpu_time"],
            c="red", s=90, edgecolors="black", label="Anomaly"
        )

        for idx, row in anomalies.iterrows():
            label = row.get("secId", "")
            plt.annotate(
                str(label),
                (xvals[idx], row["cpu_time"]),
                textcoords="offset points", xytext=(5, 5)
            )

    plt.xticks(
        ticks=range(len(df["phase_cat"].cat.categories)),
        labels=df["phase_cat"].cat.categories,
        rotation=45
    )

    plt.xlabel("Stress Type")
    plt.ylabel("CPU Time (sec)")
    plt.title("CPU Time by Stress Type (Enhanced)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

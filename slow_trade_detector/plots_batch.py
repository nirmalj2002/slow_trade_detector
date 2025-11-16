# plots_batch.py
"""
Batch-level visualizations.

Provides:
 - CPU Time vs Date (scatter)
 - Highlights batch anomalies
"""

import matplotlib.pyplot as plt
import pandas as pd


def plot_batch_cpu(df: pd.DataFrame):
    """
    Scatter plot of total CPU time over dates, highlighting anomalies.

    Expected columns:
        - date (or eodDate)
        - cpu_time_seconds
        - batch_anomaly (bool)

    Parameters
    ----------
    df : pd.DataFrame
    """

    df = df.copy()

    # Ensure date column
    if "date" not in df.columns and "eodDate" in df.columns:
        df["date"] = pd.to_datetime(df["eodDate"])

    normal = df[df["batch_anomaly"] == False]
    anomalies = df[df["batch_anomaly"] == True]

    plt.figure(figsize=(14, 6))

    # Normal points
    if not normal.empty:
        plt.scatter(
            normal["date"],
            normal["cpu_time_seconds"],
            c="blue",
            alpha=0.6,
            label="Normal",
        )

    # Anomalies
    if not anomalies.empty:
        plt.scatter(
            anomalies["date"],
            anomalies["cpu_time_seconds"],
            c="red",
            s=90,
            edgecolors="black",
            label="Batch Anomaly",
        )

        # Annotate each point with the phase
        for _, row in anomalies.iterrows():
            plt.annotate(
                row.get("phase", ""),
                (row["date"], row["cpu_time_seconds"]),
                textcoords="offset points",
                xytext=(5, 5),
            )

    plt.xlabel("EOD Date")
    plt.ylabel("Total CPU Time (sec)")
    plt.title("Batch CPU Time by Phase (Anomaly Highlighted)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

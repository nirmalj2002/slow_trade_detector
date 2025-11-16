# detector_batch.py
"""
Batch-level anomaly detection.

Input DataFrame must contain:
    eodDate (datetime)
    phase (string)
    total_grid_calls (int)
    cpu_time_seconds (float)
    cnt (number of secIds)

Output DataFrame contains:
    z-scores, rolling stats, batch_anomaly flag
"""

import pandas as pd
from .config import (
    ROLLING_WINDOW,
    ZSCORE_THRESHOLD,
    MIN_BATCH_HISTORY,
)


def detect_batch_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect anomalies at batch (EOD × phase) level.

    Rules:
      - Compute rolling median / std for CPU, CPU per secId, and total calls.
      - Compute z-scores.
      - If any z > threshold => batch_anomaly = True.

    Returns
    -------
    pd.DataFrame
    """

    df = df.copy()

    # Date normalization
    df["date"] = pd.to_datetime(df["eodDate"])
    df["day_of_week"] = df["date"].dt.day_name()

    # Derived features
    df["cpu_per_secId"] = df["cpu_time_seconds"] / df["cnt"].replace(0, pd.NA)
    df["cpu_per_call"] = df["cpu_time_seconds"] / df["total_grid_calls"].replace(0, pd.NA)

    # Internal helper: compute rolling stats safely
    def detect_for_phase(g: pd.DataFrame) -> pd.DataFrame:
        g = g.sort_values("date")

        for col in ["cpu_time_seconds", "cpu_per_secId", "total_grid_calls"]:
            roll_med = g[col].rolling(
                ROLLING_WINDOW, min_periods=MIN_BATCH_HISTORY
            ).median()
            roll_std = g[col].rolling(
                ROLLING_WINDOW, min_periods=MIN_BATCH_HISTORY
            ).std()

            g[f"{col}_roll_med"] = roll_med
            g[f"{col}_roll_std"] = roll_std
            g[f"{col}_z"] = (g[col] - roll_med) / roll_std

        # Final anomaly rule
        g["batch_anomaly"] = (
            (g["cpu_time_seconds_z"] > ZSCORE_THRESHOLD)
            | (g["cpu_per_secId_z"] > ZSCORE_THRESHOLD)
            | (g["total_grid_calls_z"] > ZSCORE_THRESHOLD)
        ).fillna(False)

        return g

    # Apply per phase
    out = df.groupby("phase", group_keys=False, sort=False).apply(
        detect_for_phase
    )
    
    out = out.reset_index(drop=True)
    
    return out

# detector_instrument.py
"""
Instrument-level slow trade detection.

Input DataFrame must contain:
    eodDate, phase, secId, num_calls, cpu_time

Output DataFrame contains:
    cross_anomaly
    ts_anomaly
    slow_trade
"""

import pandas as pd
from .config import (
    ROLLING_WINDOW,
    ZSCORE_THRESHOLD,
    MIN_HISTORY_DAYS,
)


def detect_instrument_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect anomalous instruments (slow trades).

    Two layers:
      1) Cross-sectional (same date, same phase)
      2) Time-series per secId

    Returns
    -------
    pd.DataFrame
    """

    df = df.copy()

    # Normalize dates
    df["date"] = pd.to_datetime(df["eodDate"])
    df["day_of_week"] = df["date"].dt.day_name()

    # ───────────────────────────────────────────────────────────────
    # 1. Cross-sectional anomaly per (date, phase)
    # ───────────────────────────────────────────────────────────────

    def cross_check(group):
        if len(group) < 2:
            group["cross_anomaly"] = False
            return group

        calls_p25 = group["num_calls"].quantile(0.25)
        cpu_p90 = group["cpu_time"].quantile(0.90)

        group["cross_anomaly"] = (
            (group["num_calls"] < calls_p25)
            & (group["cpu_time"] > cpu_p90)
        )

        group["cross_anomaly"] = group["cross_anomaly"].fillna(False)
        return group

    df = (
        df.groupby(["date", "phase"], group_keys=False)
        .apply(cross_check)
    )

    # ───────────────────────────────────────────────────────────────
    # 2. Time-series anomaly per secId
    # ───────────────────────────────────────────────────────────────

    def ts_check(group):
        group = group.sort_values("date")

        roll_med = group["cpu_time"].rolling(
            ROLLING_WINDOW, min_periods=MIN_HISTORY_DAYS
        ).median()
        roll_std = group["cpu_time"].rolling(
            ROLLING_WINDOW, min_periods=MIN_HISTORY_DAYS
        ).std()

        group["roll_med_cpu"] = roll_med
        group["roll_std_cpu"] = roll_std
        group["zscore_cpu"] = (group["cpu_time"] - roll_med) / roll_std
        group["ts_anomaly"] = (group["zscore_cpu"] > ZSCORE_THRESHOLD).fillna(False)

        return group

    df = (
        df.groupby("secId", group_keys=False)
        .apply(ts_check)
    )

    # ───────────────────────────────────────────────────────────────
    # 3. Final slow trade
    # ───────────────────────────────────────────────────────────────

    df["slow_trade"] = (
        df["cross_anomaly"].fillna(False)
        | df["ts_anomaly"].fillna(False)
    )

    return df

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
import warnings
from .config import (
    ROLLING_WINDOW,
    ZSCORE_THRESHOLD,
    MIN_HISTORY_DAYS,
)

# Suppress the pandas FutureWarning about groupby.apply operating on grouping
# columns. This is expected behavior for our use case (we want to preserve and
# modify grouping columns), and will be handled in a future refactor.
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    message=".*groupby.*grouping columns.*",
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
        df.groupby(["date", "phase"], group_keys=False, sort=False)
        .apply(cross_check)
    )

    # ───────────────────────────────────────────────────────────────
    # 2. Time-series anomaly per secId
    # ───────────────────────────────────────────────────────────────

    # Sort by secId and date globally to compute rolling statistics correctly
    df = df.sort_values(["secId", "date"]).reset_index(drop=True)

    # Compute rolling median and std per secId using groupby().transform()
    # This approach naturally preserves all columns in df.
    df["roll_med_cpu"] = df.groupby("secId", sort=False)["cpu_time"].transform(
        lambda x: x.rolling(ROLLING_WINDOW, min_periods=MIN_HISTORY_DAYS).median()
    )
    df["roll_std_cpu"] = df.groupby("secId", sort=False)["cpu_time"].transform(
        lambda x: x.rolling(ROLLING_WINDOW, min_periods=MIN_HISTORY_DAYS).std()
    )

    # Compute z-score and flag time-series anomalies
    df["zscore_cpu"] = (df["cpu_time"] - df["roll_med_cpu"]) / df["roll_std_cpu"]
    df["ts_anomaly"] = (df["zscore_cpu"] > ZSCORE_THRESHOLD).fillna(False)

    # ───────────────────────────────────────────────────────────────
    # 3. Final slow trade
    # ───────────────────────────────────────────────────────────────

    df["slow_trade"] = (
        df["cross_anomaly"].fillna(False)
        | df["ts_anomaly"].fillna(False)
    )

    return df

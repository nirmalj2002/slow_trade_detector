# preprocess.py
# Helper utilities for data preparation.

import pandas as pd


def add_weekly_baseline_batch(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add weekly median CPU by (phase × day_of_week) to help identify
    when Friday spikes are normal vs abnormal.

    Output column added:
      - dow_cpu_median

    Parameters
    ----------
    df : pd.DataFrame
        Must contain: phase, day_of_week, cpu_time_seconds.

    Returns
    -------
    pd.DataFrame
    """
    weekly = (
        df.groupby(["phase", "day_of_week"])["cpu_time_seconds"]
        .median()
        .rename("dow_cpu_median")
        .reset_index()
    )

    return df.merge(weekly, on=["phase", "day_of_week"], how="left")

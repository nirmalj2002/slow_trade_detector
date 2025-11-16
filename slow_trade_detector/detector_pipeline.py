# detector_pipeline.py
"""
Pipeline orchestrator connecting:

1. Batch-level anomaly detection
2. Instrument-level slow trade detection

This keeps the flow:
   batch → identify suspicious (eodDate, phase)
   instrument → analyze only those slices
"""

import pandas as pd
from typing import List, Dict, Tuple

from .detector_batch import detect_batch_anomalies
from .detector_instrument import detect_instrument_anomalies


# ───────────────────────────────────────────────────────────────
# Batch Stage
# ───────────────────────────────────────────────────────────────
def run_batch_stage(batch_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
    """
    Run batch-level detection and return:
      - batch_result: full DataFrame with metrics
      - flagged_pairs: list of {eodDate, phase} needing instrument-level scan

    Parameters
    ----------
    batch_df : pd.DataFrame

    Returns
    -------
    batch_result : pd.DataFrame
    flagged_pairs : list[dict]
    """
    batch_result = detect_batch_anomalies(batch_df)

    flagged = batch_result[batch_result["batch_anomaly"] == True]

    flagged_pairs = [
        {
            "eodDate": str(row["eodDate"].date()) if hasattr(row["eodDate"], "date") else str(row["eodDate"]),
            "phase": row["phase"],
        }
        for _, row in flagged.iterrows()
    ]

    return batch_result, flagged_pairs


# ───────────────────────────────────────────────────────────────
# Instrument Stage
# ───────────────────────────────────────────────────────────────
def run_instrument_stage(inst_df: pd.DataFrame) -> pd.DataFrame:
    """
    Run instrument-level slow trade detection.

    Parameters
    ----------
    inst_df : pd.DataFrame
        Must be instrument-level subset for one (eodDate, phase)

    Returns
    -------
    pd.DataFrame or None
    """
    if inst_df is None or inst_df.empty:
        return None

    return detect_instrument_anomalies(inst_df)

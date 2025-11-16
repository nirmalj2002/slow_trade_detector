# slow_score.py
"""
Slow trade scoring system.

Given a row with:
    cross_anomaly (bool)
    ts_anomaly (bool)
    zscore_cpu (float)

Return a 0–100 score where:
    0   => no anomaly
    100 => extremely slow / suspicious trade
"""


def slow_trade_score(row) -> int:
    """
    Combine anomaly flags and z-score into 0–100 numeric score.

    Heuristics:
      - cross anomaly  : +45 points
      - ts anomaly     : +45 points
      - high z-score   : up to +10 points

    Parameters
    ----------
    row : dict or row object

    Returns
    -------
    int : score between 0 and 100
    """
    score = 0

    if row.get("cross_anomaly"):
        score += 45

    if row.get("ts_anomaly"):
        score += 45

    # zscore contribution
    z = row.get("zscore_cpu", 0) or 0
    if z > 0:
        # scale z to at most 10 points when z is very large
        score += min(int((z / 5) * 10), 10)

    return min(score, 100)

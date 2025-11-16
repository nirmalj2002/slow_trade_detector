# config.py
# Central tunables for anomaly detection.

# Rolling window for medians / std dev (in days)
ROLLING_WINDOW = 7

# z-score threshold beyond which we call something anomalous
ZSCORE_THRESHOLD = 2.0

# Minimum number of data points required before rolling stats are meaningful
MIN_HISTORY_DAYS = 3

# Minimum history specifically for batch-level rolling stats
MIN_BATCH_HISTORY = 3

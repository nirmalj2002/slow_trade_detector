# loader_sybase.py
# Sybase database loader using pyodbc.
# Replace CONN_STR with your real DSN or connection string.

import pandas as pd
import pyodbc

# Example ODBC DSN connection string — update to your environment
CONN_STR = "DSN=YOUR_SYBASE_DSN;UID=your_user;PWD=your_password"


def get_conn():
    """
    Returns a live pyodbc connection to Sybase.
    """
    return pyodbc.connect(CONN_STR)


def load_batch_from_sybase() -> pd.DataFrame:
    """
    Loads batch-level aggregated summary.

    Expected output columns:
      eodDate, phase, total_grid_calls, cpu_time_seconds, cnt (# secIds)

    This is extremely lightweight and scalable.
    """
    query = """
    SELECT
        CONVERT(VARCHAR(10), eodDate, 23) AS eodDate,
        phase,
        SUM(calls) AS total_grid_calls,
        SUM(cpuTime) AS cpu_time_seconds,
        COUNT(DISTINCT secId) AS cnt
    FROM calcStatistics
    GROUP BY CONVERT(VARCHAR(10), eodDate, 23), phase
    ORDER BY eodDate, phase
    """

    conn = get_conn()
    df = pd.read_sql(query, conn)

    # Normalize types
    df["eodDate"] = pd.to_datetime(df["eodDate"])
    df["date"] = df["eodDate"]
    df["day_of_week"] = df["date"].dt.day_name()

    return df


def load_instrument_from_sybase(eodDate, phase) -> pd.DataFrame:
    """
    Loads instrument-level rows for a given (eodDate, phase).

    Expected columns:
      eodDate, phase, secId, num_calls, cpu_time
    """
    query = """
    SELECT
        CONVERT(VARCHAR(10), eodDate, 23) AS eodDate,
        phase,
        secId,
        calls AS num_calls,
        cpuTime AS cpu_time
    FROM calcStatistics
    WHERE CONVERT(VARCHAR(10), eodDate, 23) = ?
      AND phase = ?
    """

    conn = get_conn()
    df = pd.read_sql(query, conn, params=[str(pd.to_datetime(eodDate).date()), phase])

    df["eodDate"] = pd.to_datetime(df["eodDate"])
    df["date"] = df["eodDate"]
    df["day_of_week"] = df["date"].dt.day_name()

    return df

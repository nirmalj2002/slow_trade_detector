# loader.py
# Local CSV loader with date normalization.

import pandas as pd


def load_csv(path: str, date_col: str = "eodDate") -> pd.DataFrame:
    """
    Loads a CSV file and ensures:
      - eodDate exists and is parsed as datetime
      - date column is created
      - day_of_week column is added

    Parameters
    ----------
    path : str
        Path to CSV file.
    date_col : str, optional
        Column name containing the date.

    Returns
    -------
    pd.DataFrame
    """
    df = pd.read_csv(path)

    # Normalize date column
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col])
    elif "date" in df.columns:
        df["eodDate"] = pd.to_datetime(df["date"])
    else:
        raise ValueError(
            "CSV must contain either 'eodDate' or 'date' column."
        )

    df["date"] = df["eodDate"]
    df["day_of_week"] = df["date"].dt.day_name()

    return df

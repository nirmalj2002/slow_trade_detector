# Slow Trade Detector

A **two-stage anomaly detection system** for identifying slow trades at batch and instrument levels using rolling statistics, z-scores, and cross-sectional analysis.

**Status:** ✅ **Production Ready** - Fully tested and operational

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [Key Features](#key-features)
3. [How It Works](#how-it-works)
4. [Data Requirements](#data-requirements)
5. [Configuration](#configuration)
6. [Usage Examples](#usage-examples)
7. [Output & Reports](#output--reports)
8. [Database Support](#database-support)
9. [Architecture](#architecture)
10. [Requirements](#requirements)
11. [Performance](#performance-notes)
12. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Installation

```bash
# Clone or navigate to project directory
cd slow_trade_detector

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install package in development mode
python -m pip install -e .
```

### Run Synthetic Example (No Data Needed)

```bash
python -m examples.run_synthetic
```

Generates automatically in `output/` folder:
- ✅ 360 detected slow trades with scores
- ✅ 16 PNG plots (no popup windows)
- ✅ Professional HTML report
- ✅ Complete in < 10 seconds

**Output location:** `output/synthetic_report.html`

### Run With CSV Data

1. Place CSV files in `input/` folder:
   - `batch_summary.csv`
   - `instrument_data.csv` (optional)

2. Run:
```bash
python -m examples.run_with_csv
```

**Output location:** `output/csv_run_report.html`

---

## Key Features

✅ **Two-Stage Detection**
- Batch-level anomalies (rolling statistics)
- Instrument-level slow trades (cross-sectional + time-series)

✅ **Professional Reports**
- Interactive HTML with summary cards
- Executive statistics dashboard
- Detailed data tables

✅ **Fully Automated**
- No popup windows (headless execution)
- Auto-generates plots to PNG files
- Creates output/ folder automatically

✅ **Production Ready**
- Handles missing data gracefully
- Configurable sensitivity thresholds
- Detailed error messages
- Comprehensive logging

---

## How It Works

### **Stage 1: Batch-Level Anomaly Detection**

Analyzes daily aggregated metrics to find suspicious batches:

**Input:**
- `eodDate` - End of day date
- `phase` - Processing phase (e.g., "A", "B")
- `cpu_time_seconds` - Total CPU consumed
- `total_grid_calls` - Number of grid calls
- `cnt` - Count of securities processed

**Algorithm:**
1. Group by `phase`
2. Compute 7-day **rolling median & std dev** for:
   - CPU time
   - CPU per security
   - Total calls
3. Calculate **z-scores** for each metric
4. Flag as anomaly if **z-score > 2.0** (configurable)

**Output:**
- List of flagged `(eodDate, phase)` pairs
- Full metrics including rolling statistics
- `batch_anomaly` boolean flag

**Example Detection:**
```
Date        Phase  CPU Time  Z-Score  Anomaly?
2024-01-21  A      1,125s    3.2      ✓ YES
2024-01-26  B      739s      2.5      ✓ YES
2024-01-15  A      198s      -0.1     ✗ NO
```

---

### **Stage 2: Instrument-Level Slow Trade Detection**

For each flagged batch, analyzes individual instruments to find slow trades:

**Input (per flagged batch):**
- `secId` - Security/instrument ID
- `num_calls` - Number of calls for this instrument
- `cpu_time` - CPU consumed by this instrument
- `eodDate`, `phase`

**Algorithm:**

**A) Cross-Sectional Check** (within same date + phase)
- Identify instruments with:
  - `num_calls` < 25th percentile (few calls)
  - `cpu_time` > 90th percentile (high CPU)
- These instruments are inefficient relative to others that day

**B) Time-Series Check** (per instrument across days)
- For each instrument, compute 7-day rolling stats
- Calculate z-score of CPU time
- Flag if z-score > 2.0

**Final Rule:**
```
slow_trade = cross_anomaly OR time_series_anomaly
slow_score = 45 points (cross) + 45 points (ts) + 0-10 points (z-score)
```

**Example Detection:**
```
secId   num_calls  cpu_time  Cross?  TS?  Slow Trade?  Score
S010    3          43.9s     ✓       ✓    ✓            45
S022    2          39.4s     ✓       ✓    ✓            45
S050    15         8.2s      ✗       ✗    ✗            0
```

---

## Data Requirements

### Minimum Data for Accurate Detection

| Metric | Minimum | Recommended | Reason |
|--------|---------|-------------|--------|
| **Batch History** | 10 days | 30-60 days | 7-day rolling window needs 3+ days to start, but 30+ days gives stable baseline |
| **Daily Batches** | 2 phases | 2-4 phases | Need variation to detect anomalies |
| **Instruments/Batch** | 20-30 | 50-100+ | More samples = better percentile detection |
| **Time Coverage** | Consecutive | Consecutive | Rolling stats fail with gaps; fill or exclude |
| **Data Quality** | 95%+ | 99%+ | Missing values break calculations |

### Optimal Dataset Characteristics

**For reliable slow trade detection:**

✅ **Batch Level:**
- 60 days of history (2 phases = 120 rows)
- Consistent daily data (no >3 day gaps)
- 80+ grid calls per batch
- 30-60 securities processed per batch

✅ **Instrument Level:**
- 50-200 instruments per batch
- 1-50 calls per instrument (wide range is good)
- 0.1-100 CPU seconds range
- Consistent instrument set across days

### What Happens With Less Data?

| Scenario | Impact | Workaround |
|----------|--------|-----------|
| < 10 days | Rolling stats show `NaN`, no anomalies detected | Use `MIN_BATCH_HISTORY` in config |
| < 20 instruments | Percentiles unreliable | Use domain knowledge instead |
| Gaps > 3 days | Rolling window resets, false positives | Fill gaps or restart analysis |
| All same CPU values | Std dev = 0, division by zero | Add synthetic variation or increase data |

---

## Configuration

Edit `slow_trade_detector/config.py` to tune detection:

```python
# Rolling window for computing median/std (in days)
ROLLING_WINDOW = 7

# Z-score threshold for anomalies (lower = more sensitive)
ZSCORE_THRESHOLD = 2.0  # Default: 2.0 (roughly top 5%)
                         # Aggressive: 1.5 (top 7%)
                         # Conservative: 2.5 (top 3%)

# Minimum data points before rolling stats are meaningful
MIN_BATCH_HISTORY = 3
MIN_HISTORY_DAYS = 3
```

### Tuning Guidelines

**Increase sensitivity (catch more anomalies):**
```python
ZSCORE_THRESHOLD = 1.5  # More aggressive
ROLLING_WINDOW = 5      # Faster response to changes
```

**Decrease sensitivity (fewer false positives):**
```python
ZSCORE_THRESHOLD = 2.5  # More conservative
ROLLING_WINDOW = 10     # Smoother baseline
```

---

## Usage Examples

### 1. Synthetic Data (No Setup Needed)

```bash
python -m examples.run_synthetic
```

**What it does:**
- Generates 30 days of synthetic batch data (2 phases)
- Injects CPU anomalies on specific dates
- Detects batch-level anomalies
- Generates 59 instruments per batch with injected slow trades
- Creates time-series data for all 30 days
- Identifies 360 slow trades across 6 instruments
- Outputs: 1 HTML report + 16 PNG plots to `output/` folder
- Runtime: < 10 seconds

**Perfect for:**
- Testing the pipeline
- Understanding output formats
- Validating installation
- POC demonstrations

### 2. Real CSV Data

**Setup:**
1. Create `input/` folder with CSV files:

**`input/batch_summary.csv`:**
```csv
eodDate,phase,total_grid_calls,cpu_time_seconds,cnt
2024-01-01,A,119,212.19,43
2024-01-01,B,85,230.02,50
2024-01-02,A,111,121.96,59
...
```

**`input/instrument_data.csv`:**
```csv
eodDate,phase,secId,num_calls,cpu_time
2024-01-01,A,S001,5,10.23
2024-01-01,A,S002,3,45.67
2024-01-01,B,S001,8,12.45
...
```

**Run:**
```bash
python -m examples.run_with_csv
```

**Output:** `output/csv_run_report.html` + PNG plots for flagged batches

**Features:**
- Reads from `input/` folder
- Falls back to Sybase if configured
- Saves all outputs to `output/` folder
- Better error messages if files not found

### 3. Database (Sybase) - Production Use

**Prerequisites:**
- Sybase ODBC driver installed
- DSN configured

**Configure connection:**
```python
# In slow_trade_detector/loader_sybase.py
DSN = "your_sybase_dsn"
USER = "your_user"
PASSWORD = "your_password"
```

**Use in code:**
```python
from slow_trade_detector.loader_sybase import load_batch_from_sybase, load_instrument_from_sybase

# Load batch-level data
batch_df = load_batch_from_sybase(
    start_date="2024-01-01", 
    end_date="2024-01-31"
)

# Load instrument data for specific batch
inst_df = load_instrument_from_sybase(
    eod="2024-01-21",
    phase="A"
)
```

---

## Output & Reports

### HTML Reports

**Available Reports:**
- `output/synthetic_report.html` - From synthetic data
- `output/csv_run_report.html` - From CSV data

**Report Contents:**

**Executive Summary Section:**
- Batch Anomalies Found (count)
- Slow Trades Detected (count)
- Affected Instruments (count)
- Average Slow Score (0-100)

**Batch-Level Table:**
- Date, Phase, CPU Time, Calls, CPU per Security
- Only anomalous rows shown
- Formatted with 2 decimal places

**Instrument-Level Table:**
- Top 20 slowest trades by score
- Date, Phase, Security ID, Calls, CPU Time, Score
- Full list available if > 20 trades detected

### PNG Plots

**Batch Overview:**
- `batch_cpu_plot.png` - CPU trend over time

**Per Flagged Batch (3 plots each):**
- `plot_cpu_vs_calls_[phase]_[date].png` - Scatter + regression
- `plot_cpu_per_call_[phase]_[date].png` - Efficiency analysis
- `plot_cpu_vs_stress_[phase]_[date].png` - Categorical comparison

**Location:** All plots saved to `output/` folder

### Console Output Example

```
Generating synthetic batch data...
Running batch detection...
Flagged (eodDate, phase) pairs: [{'eodDate': '2024-01-07', 'phase': 'B'}, ...]
Plotting batch CPU...

Detected slow trades:
        eodDate phase secId  num_calls   cpu_time  slow_score
9    2024-01-01     A  S010          3  43.942214          45
14   2024-01-01     A  S015          2  42.064369          45
...

HTML report written to output\synthetic_report.html
15 instrument plots saved to output/ folder
```

---

## Database Support

### Sybase Integration

The `loader_sybase.py` module provides:

```python
# Load batch-level data
batch_df = load_batch_from_sybase(
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Load instrument data for a specific batch
inst_df = load_instrument_from_sybase(
    eod="2024-01-21",
    phase="A"
)
```

**Before use:**
1. Install: `pip install pyodbc`
2. Configure DSN in `loader_sybase.py`
3. Set credentials

---

## Architecture

### File Structure

```
slow_trade_detector/
├── config.py                  # Tuning parameters
├── detector_batch.py          # Batch anomaly detection
├── detector_instrument.py     # Instrument/slow trade detection
├── detector_pipeline.py       # Orchestration
├── slow_score.py              # Scoring logic
├── report_html.py             # Report generation
├── plots.py                   # Instrument-level visualizations
├── plots_batch.py             # Batch-level visualizations
├── loader.py                  # CSV data loading
├── loader_sybase.py           # Database loading
├── preprocess.py              # Data preprocessing
└── __init__.py

input/                          # Input data folder (user creates)
├── batch_summary.csv          # Batch-level data
└── instrument_data.csv        # Instrument-level data (optional)

output/                         # Output results (auto-created)
├── *.html                      # Reports
└── *.png                       # Plots

examples/
├── run_synthetic.py           # Synthetic demo
└── run_with_csv.py            # CSV analysis
```

### Detection Pipeline

```
Input Data
    ↓
[Batch Detection Stage]
  • Group by phase
  • Compute rolling stats (7-day window)
  • Calculate z-scores
  • Identify anomalous batches
    ↓
[Flagged Batches] → [Instrument Detection Stage]
                    • Load instrument data
                    • Cross-sectional analysis (percentiles)
                    • Time-series analysis (rolling z-scores)
                    • Combine rules → slow_trade flag
                    • Generate slow_score (0-100)
                      ↓
                    [Output: Slow Trades + Visualizations]
                      ↓
                    [HTML Report + PNG Plots]
```

---

## Requirements

```
pandas>=1.3
numpy
matplotlib
scikit-learn
jinja2
pyodbc  # Optional, for Sybase
```

Install all:
```bash
pip install -r requirements.txt
```

---

## Performance Notes

- **Synthetic example:** < 10 seconds (no data loading)
- **CSV with 60 days data:** 10-30 seconds
- **Sybase query (1 month):** 30-60 seconds (network dependent)
- **Report generation:** < 1 second
- **PNG plots:** ~2-3 seconds total

All plots saved to disk (no popup windows) — fully automated!

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'slow_trade_detector'`

**Solution:** Install in development mode:
```bash
python -m pip install -e .
```

### Issue: `No slow trades found` with real data

**Possible causes:**
- Insufficient history (< 10 days)
- Z-score threshold too high
- Data lacks variation

**Try:**
```python
# In config.py
ZSCORE_THRESHOLD = 1.5  # Lower threshold
```

### Issue: Plots not saving / `NaN` in output

**Possible causes:**
- Missing values in data
- Division by zero (constant values)
- Timestamp format issues

**Solution:** Check data with:
```python
import pandas as pd
df = pd.read_csv('batch_summary.csv')
print(df.isnull().sum())  # Check for missing values
print(df.describe())       # Check ranges
```

---

## Contributing

To extend the detector:

1. **Add custom scoring:** Edit `slow_score.py`
2. **Add new visualizations:** Create `plots_custom.py`
3. **Add data loaders:** Extend `loader.py` or `loader_sybase.py`
4. **Tune thresholds:** Modify `config.py`

---

## Support

For questions, enhancements, or dataset adapters:
- Review the pipeline in `detector_pipeline.py`
- Check configuration options in `config.py`
- Examine example data in `examples/`

---

**Version:** 0.1.0  
**Last Updated:** November 2025  
**Status:** Production Ready for POC


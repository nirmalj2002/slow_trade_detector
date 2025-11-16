# run_synthetic.py
"""
Synthetic example demonstrating:
  - Batch-level anomaly detection
  - Instrument-level anomaly detection
  - Plotting
  - Scoring
  - HTML report output

Run:
    python examples/run_synthetic.py
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend - no windows will pop up
import os

from slow_trade_detector.detector_pipeline import (
    run_batch_stage,
    run_instrument_stage,
)
from slow_trade_detector.slow_score import slow_trade_score
from slow_trade_detector.report_html import render_html_report
from slow_trade_detector.plots_batch import plot_batch_cpu
from slow_trade_detector.plots import (
    plot_cpu_vs_calls_enhanced,
    plot_cpu_per_call_enhanced,
    plot_cpu_vs_stress_enhanced,
)


# -------------------------------------------------------------
# 1. Create synthetic batch-level data
# -------------------------------------------------------------
def generate_synthetic_batch():
    dates = pd.date_range("2024-01-01", periods=30, freq="D")
    phases = ["A", "B"]

    rows = []
    rng = np.random.default_rng(42)

    for d in dates:
        for ph in phases:
            base_cpu = rng.normal(200, 40)
            calls = rng.integers(80, 140)
            cnt = rng.integers(30, 60)

            # Inject multiple strong anomalies
            if d == dates[20] and ph == "A":
                base_cpu *= 5  # very big spike
            elif d == dates[15] and ph == "B":
                base_cpu *= 4.5  # another big anomaly
            elif d == dates[25]:
                base_cpu *= 4  # yet another spike

            rows.append({
                "eodDate": d,
                "phase": ph,
                "total_grid_calls": calls,
                "cpu_time_seconds": max(base_cpu, 1),
                "cnt": cnt,
            })

    return pd.DataFrame(rows)


# -------------------------------------------------------------
# 2. Create synthetic instrument-level data
# -------------------------------------------------------------
def generate_synthetic_instruments(eod, phase):
    rng = np.random.default_rng(99)

    rows = []
    sec_ids = [f"S{i:03d}" for i in range(1, 60)]

    for sec in sec_ids:
        calls = rng.integers(1, 20)
        cpu = rng.normal(10, 3)

        # Inject multiple anomalies to create slow trades
        if sec in ["S010", "S022"]:
            cpu *= 4  # high CPU with few calls = slow trade
            calls = max(int(calls / 2), 1)
        elif sec in ["S015", "S033"]:
            cpu *= 3.5  # another slow trade pattern
            calls = max(int(calls / 3), 1)
        elif sec == "S045":
            cpu *= 5  # severe slow trade
            calls = 1

        rows.append({
            "eodDate": pd.to_datetime(eod),
            "phase": phase,
            "secId": sec,
            "num_calls": max(int(calls), 1),
            "cpu_time": float(max(cpu, 0.1)),
        })

    return pd.DataFrame(rows)


# -------------------------------------------------------------
# MAIN RUN
# -------------------------------------------------------------
def main(show_plots=False):
    """
    Run the synthetic detection example.
    
    Parameters
    ----------
    show_plots : bool
        If True, display matplotlib plots (creates many windows).
        If False, save plots to PNG files instead.
    """
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)

    print("Generating synthetic batch data...")
    batch_df = generate_synthetic_batch()

    print("Running batch detection...")
    batch_result, flagged_pairs = run_batch_stage(batch_df)
    print("Flagged (eodDate, phase) pairs:", flagged_pairs)

    print("Plotting batch CPU...")
    plot_batch_cpu(batch_result)
    if not show_plots:
        import matplotlib.pyplot as plt
        plt.savefig(os.path.join("output", "batch_cpu_plot.png"), dpi=150, bbox_inches='tight')
        plt.close()

    # Instrument-level analysis on all batch pairs to build time series
    all_inst_results = []

    # Generate data for all dates to build time series
    dates = pd.date_range("2024-01-01", periods=30, freq="D")
    phases = ["A", "B"]
    
    plot_count = 0
    for phase in phases:
        all_phase_instruments = []
        
        for date in dates:
            inst_df = generate_synthetic_instruments(date, phase)
            all_phase_instruments.append(inst_df)
        
        # Combine all data for this phase to get time series
        combined_df = pd.concat(all_phase_instruments, ignore_index=True)
        
        # Run instrument detection on the full time series
        inst_result = run_instrument_stage(combined_df)
        inst_result["slow_score"] = inst_result.apply(slow_trade_score, axis=1)
        
        all_inst_results.append(inst_result)
        
        # Only visualize flagged pairs
        for pair in flagged_pairs:
            eod_str = pair["eodDate"]
            eod_date = pd.to_datetime(eod_str)
            pair_phase = pair["phase"]
            
            if pair_phase == phase:
                subset = inst_result[inst_result["eodDate"] == eod_date]
                if not subset.empty:
                    plot_cpu_vs_calls_enhanced(subset)
                    if not show_plots:
                        import matplotlib.pyplot as plt
                        plt.savefig(os.path.join("output", f"plot_cpu_vs_calls_{pair_phase}_{eod_str}.png"), dpi=150, bbox_inches='tight')
                        plt.close()
                    plot_count += 1
                    
                    plot_cpu_per_call_enhanced(subset)
                    if not show_plots:
                        import matplotlib.pyplot as plt
                        plt.savefig(os.path.join("output", f"plot_cpu_per_call_{pair_phase}_{eod_str}.png"), dpi=150, bbox_inches='tight')
                        plt.close()
                    plot_count += 1
                    
                    plot_cpu_vs_stress_enhanced(subset)
                    if not show_plots:
                        import matplotlib.pyplot as plt
                        plt.savefig(os.path.join("output", f"plot_cpu_vs_stress_{pair_phase}_{eod_str}.png"), dpi=150, bbox_inches='tight')
                        plt.close()
                    plot_count += 1

    if all_inst_results:
        final_inst = pd.concat(all_inst_results, ignore_index=True)
        slow = final_inst[final_inst["slow_trade"] == True]

        print("\nDetected slow trades:")
        if not slow.empty:
            print(slow[["eodDate", "phase", "secId", "num_calls", "cpu_time", "slow_score"]])
        else:
            print("No slow trades found in detailed analysis.")

        # Generate HTML report
        html = render_html_report(batch_result, slow)
        report_path = os.path.join("output", "synthetic_report.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"\nHTML report written to {report_path}")
        
        if not show_plots:
            print(f"{plot_count} instrument plots saved to output/ folder")
    else:
        print("\nNo slow trades found.")


if __name__ == "__main__":
    main()

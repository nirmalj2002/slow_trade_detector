# run_with_csv.py
"""
Example: Run the slow trade pipeline using real CSV inputs.

Expected CSV files in input/ folder:
  - batch_summary.csv   (batch-level aggregated data)
  - instrument_data.csv (optional full instrument dump)

Output files saved to output/ folder:
  - csv_run_report.html (summary report)
  - PNG plot files

If instrument-level data is large, you typically load only the
(EOD, phase) pairs flagged by batch detection.
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend - no windows will pop up
import warnings

# Suppress non-critical warnings (matplotlib headless mode, etc.)
warnings.filterwarnings("ignore", category=UserWarning, message=".*non-interactive.*")

from slow_trade_detector.loader import load_csv
from slow_trade_detector.loader_sybase import load_instrument_from_sybase
from slow_trade_detector.detector_pipeline import (
    run_batch_stage,
    run_instrument_stage,
)
from slow_trade_detector.slow_score import slow_trade_score
from slow_trade_detector.plots_batch import plot_batch_cpu
from slow_trade_detector.plots import (
    plot_cpu_vs_calls_enhanced,
    plot_cpu_per_call_enhanced,
    plot_cpu_vs_stress_enhanced,
)
from slow_trade_detector.report_html import render_html_report
import os


def main(show_plots=False):
    """
    Run CSV-based detection example.
    
    Parameters
    ----------
    show_plots : bool
        If True, display matplotlib plots (creates windows).
        If False, save plots to PNG files instead.
    """
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)

    # Construct paths to input files
    batch_csv = os.path.join("input", "batch_summary.csv")
    instrument_csv = os.path.join("input", "instrument_data.csv")

    # Check if input files exist
    if not os.path.exists(batch_csv):
        print(f"Error: {batch_csv} not found!")
        print("Please place batch_summary.csv in the input/ folder")
        return

    # Load batch-level CSV (user-provided)
    print(f"Loading {batch_csv} ...")
    batch_df = load_csv(batch_csv)

    # Run batch detection
    print("Running batch anomaly detection ...")
    batch_result, flagged_pairs = run_batch_stage(batch_df)

    print("\nFlagged (eodDate, phase) pairs:")
    for p in flagged_pairs:
        print(" -", p)

    # Plot batch CPU
    print("Plotting batch CPU ...")
    plot_batch_cpu(batch_result)
    if not show_plots:
        import matplotlib.pyplot as plt
        plt.savefig(os.path.join("output", "batch_cpu_plot.png"), dpi=150, bbox_inches='tight')
        plt.close()

    # Run instrument-level detection for flagged pairs
    all_inst_results = []
    plot_count = 0

    for pair in flagged_pairs:
        eod = pair["eodDate"]
        phase = pair["phase"]

        print(f"\nFetching instrument-level data for {eod} | {phase} ...")

        # Option 1: Load from Sybase (recommended for production)
        inst_df = None
        try:
            inst_df = load_instrument_from_sybase(eod, phase)
        except Exception as e:
            print(f"  Sybase connection failed: {e}")

        # Option 2: Local CSV fallback
        if inst_df is None or inst_df.empty:
            if os.path.exists(instrument_csv):
                try:
                    inst_all = load_csv(instrument_csv)
                    inst_df = inst_all[
                        (inst_all["eodDate"].astype(str) == eod)
                        & (inst_all["phase"] == phase)
                    ]
                    if not inst_df.empty:
                        print(f"  Loaded {len(inst_df)} instruments from {instrument_csv}")
                except Exception as e:
                    print(f"  CSV load failed: {e}")
                    inst_df = None
            else:
                print(f"  {instrument_csv} not found in input/ folder")

        if inst_df is None or inst_df.empty:
            print(f"  No instrument data found for {eod} | {phase}")
            continue

        result = run_instrument_stage(inst_df)
        result["slow_score"] = result.apply(slow_trade_score, axis=1)
        all_inst_results.append(result)

        # Visualizations
        print(f"  Generating visualizations...")
        plot_cpu_vs_calls_enhanced(result)
        if not show_plots:
            import matplotlib.pyplot as plt
            plt.savefig(os.path.join("output", f"plot_cpu_vs_calls_{phase}_{eod}.png"), dpi=150, bbox_inches='tight')
            plt.close()
        plot_count += 1

        plot_cpu_per_call_enhanced(result)
        if not show_plots:
            import matplotlib.pyplot as plt
            plt.savefig(os.path.join("output", f"plot_cpu_per_call_{phase}_{eod}.png"), dpi=150, bbox_inches='tight')
            plt.close()
        plot_count += 1

        plot_cpu_vs_stress_enhanced(result)
        if not show_plots:
            import matplotlib.pyplot as plt
            plt.savefig(os.path.join("output", f"plot_cpu_vs_stress_{phase}_{eod}.png"), dpi=150, bbox_inches='tight')
            plt.close()
        plot_count += 1

    # Save results
    if not all_inst_results:
        print("\nNo instrument-level slow trades found.")
        return

    final_inst = pd.concat(all_inst_results, ignore_index=True)
    slow = final_inst[final_inst["slow_trade"] == True]

    print("\n" + "="*70)
    print("DETECTED SLOW TRADES")
    print("="*70)
    if not slow.empty:
        print(slow[["eodDate", "phase", "secId", "num_calls", "cpu_time", "slow_score"]].to_string())
        print(f"\nTotal slow trades: {len(slow)}")
    else:
        print("No slow trades found in detailed analysis.")

    # HTML output
    html = render_html_report(batch_result, slow)
    report_path = os.path.join("output", "csv_run_report.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nHTML report saved to {report_path}")
    
    if not show_plots and plot_count > 0:
        print(f"{plot_count} instrument plots saved to output/ folder")


if __name__ == "__main__":
    main()

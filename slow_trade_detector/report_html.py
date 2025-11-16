# report_html.py
"""
HTML report generator for batch and instrument anomalies.
Uses Jinja2 templating with enhanced styling and visualizations.
"""

from jinja2 import Template
import pandas as pd

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Slow Trade Detector - Daily Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, #1c4e80 0%, #2a6fa6 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .timestamp {
            opacity: 0.9;
            font-size: 0.9em;
        }
        
        .section {
            background: white;
            padding: 25px;
            margin-bottom: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        h2 {
            color: #1c4e80;
            border-bottom: 3px solid #2a6fa6;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        h3 {
            color: #2a6fa6;
            margin-top: 20px;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        
        .card.alert {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        
        .card.success {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        
        .card-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .card-label {
            opacity: 0.9;
            font-size: 0.9em;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 0.95em;
        }
        
        th {
            background-color: #f0f4f8;
            color: #1c4e80;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #2a6fa6;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        
        tr:hover {
            background-color: #f9fbfd;
        }
        
        .severity-high {
            color: #d32f2f;
            font-weight: 600;
        }
        
        .severity-medium {
            color: #f57c00;
            font-weight: 600;
        }
        
        .severity-low {
            color: #388e3c;
            font-weight: 600;
        }
        
        .chart-container {
            position: relative;
            height: 400px;
            margin: 20px 0;
        }
        
        .no-data {
            color: #999;
            font-style: italic;
            padding: 20px;
            text-align: center;
            background: #f9f9f9;
            border-radius: 4px;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
            margin-right: 5px;
        }
        
        .badge-anomaly {
            background: #ffcdd2;
            color: #c62828;
        }
        
        .badge-normal {
            background: #c8e6c9;
            color: #2e7d32;
        }
        
        footer {
            text-align: center;
            color: #666;
            padding: 20px;
            font-size: 0.85em;
        }
    </style>
</head>

<body>

<div class="container">
    <header>
        <h1>Slow Trade Detector - Daily Report</h1>
        <div class="timestamp">Generated: {{ timestamp }}</div>
    </header>

    <!-- Summary Section -->
    <div class="section">
        <h2>Executive Summary</h2>
        <div class="summary-cards">
            <div class="card alert">
                <div class="card-label">Batch Anomalies</div>
                <div class="card-value">{{ batch_anomaly_count }}</div>
            </div>
            <div class="card alert">
                <div class="card-label">Slow Trades Detected</div>
                <div class="card-value">{{ slow_trade_count }}</div>
            </div>
            <div class="card">
                <div class="card-label">Affected Instruments</div>
                <div class="card-value">{{ affected_instruments }}</div>
            </div>
            <div class="card success">
                <div class="card-label">Avg Slow Score</div>
                <div class="card-value">{{ avg_slow_score }}</div>
            </div>
        </div>
    </div>

    <!-- Batch Anomalies Section -->
    <div class="section">
        <h2>Batch-Level Anomalies</h2>
        {% if batch_table %}
            <p><strong>{{ batch_anomaly_count }} anomalous batches detected</strong></p>
            {{ batch_table | safe }}
        {% else %}
            <div class="no-data">No batch anomalies detected.</div>
        {% endif %}
    </div>

    <!-- Instrument Anomalies Section -->
    <div class="section">
        <h2>Instrument-Level Slow Trades</h2>
        {% if inst_table %}
            <p><strong>{{ slow_trade_count }} slow trades detected across {{ affected_instruments }} instruments</strong></p>
            
            <h3>Top 20 Slowest Trades (by score)</h3>
            {{ inst_table | safe }}
            
            {% if show_all_trades %}
            <h3>All Detected Slow Trades</h3>
            {{ all_inst_table | safe }}
            {% endif %}
        {% else %}
            <div class="no-data">No instrument anomalies detected.</div>
        {% endif %}
    </div>

    <footer>
        <p>Slow Trade Detector v0.1 | Powered by Pandas & Jinja2</p>
    </footer>
</div>

</body>
</html>
"""

def render_html_report(batch_df=None, inst_df=None) -> str:
    """
    Render an enhanced HTML report combining batch and instrument anomalies.

    Parameters
    ----------
    batch_df : pd.DataFrame or None
    inst_df : pd.DataFrame or None

    Returns
    -------
    str : HTML content
    """
    from datetime import datetime
    
    # Process batch data
    batch_table = ""
    batch_anomaly_count = 0
    if isinstance(batch_df, pd.DataFrame) and not batch_df.empty:
        batch_anomalies = batch_df[batch_df.get("batch_anomaly", False) == True]
        batch_anomaly_count = len(batch_anomalies)
        
        if batch_anomaly_count > 0:
            # Show only key columns
            display_cols = ["eodDate", "phase", "cpu_time_seconds", "total_grid_calls", "cpu_per_secId", "batch_anomaly"]
            available_cols = [col for col in display_cols if col in batch_anomalies.columns]
            batch_display = batch_anomalies[available_cols].copy()
            
            # Format floats
            for col in batch_display.select_dtypes(include=['float64', 'float32']).columns:
                batch_display[col] = batch_display[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
            
            batch_table = batch_display.to_html(index=False, border=0, classes="anomaly-table")
    
    # Process instrument data
    inst_table = ""
    all_inst_table = ""
    slow_trade_count = 0
    affected_instruments = 0
    avg_slow_score = 0
    
    if isinstance(inst_df, pd.DataFrame) and not inst_df.empty:
        slow_trades = inst_df[inst_df.get("slow_trade", False) == True]
        slow_trade_count = len(slow_trades)
        
        if slow_trade_count > 0:
            affected_instruments = slow_trades["secId"].nunique()
            avg_slow_score = int(slow_trades.get("slow_score", pd.Series(0)).mean())
            
            # Top 20 slow trades
            display_cols = ["eodDate", "phase", "secId", "num_calls", "cpu_time", "slow_score"]
            available_cols = [col for col in display_cols if col in slow_trades.columns]
            
            top_20 = slow_trades[available_cols].nlargest(20, "slow_score") if "slow_score" in slow_trades.columns else slow_trades[available_cols].head(20)
            
            # Format for display
            for col in top_20.select_dtypes(include=['float64', 'float32']).columns:
                top_20[col] = top_20[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
            
            inst_table = top_20.to_html(index=False, border=0, classes="slow-trades-table")
            
            # All trades for those who want full data
            all_slow = slow_trades[available_cols].copy()
            for col in all_slow.select_dtypes(include=['float64', 'float32']).columns:
                all_slow[col] = all_slow[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
            
            all_inst_table = all_slow.to_html(index=False, border=0, classes="all-trades-table")
    
    template = Template(HTML_TEMPLATE)
    
    return template.render(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        batch_table=batch_table,
        batch_anomaly_count=batch_anomaly_count,
        inst_table=inst_table,
        all_inst_table=all_inst_table,
        slow_trade_count=slow_trade_count,
        affected_instruments=affected_instruments,
        avg_slow_score=avg_slow_score,
        show_all_trades=(slow_trade_count > 20)
    )


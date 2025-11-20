#!/usr/bin/env python3
# ingest_to_duckdb.py
# Usage: python3 ingest_to_duckdb.py <db_path> <deps.json> <runs.csv> [logs_dir]

import sys, json, duckdb, pandas as pd, os

db = sys.argv[1]
deps_file = sys.argv[2]
runs_file = sys.argv[3]
logs_dir = sys.argv[4] if len(sys.argv) > 4 else None

con = duckdb.connect(db)

# create tables
con.execute("""
CREATE TABLE IF NOT EXISTS job_dependencies (
  job TEXT,
  parent TEXT
);
""")
con.execute("""
CREATE TABLE IF NOT EXISTS job_runs (
  job TEXT,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  duration_seconds DOUBLE,
  status TEXT
);
""")
con.execute("""
CREATE TABLE IF NOT EXISTS job_logs (
  job TEXT,
  run_date TIMESTAMP,
  log TEXT
);
""")

# load deps
with open(deps_file) as f:
    deps = json.load(f)
rows = []
for job, parents in deps.items():
    for p in parents:
        rows.append((job, p))
df_deps = pd.DataFrame(rows, columns=['job','parent'])
if not df_deps.empty:
    con.register('df_deps', df_deps)
    con.execute("INSERT INTO job_dependencies SELECT * FROM df_deps")

# load runs.csv
df_runs = pd.read_csv(runs_file, parse_dates=['start_time','end_time'])
con.register('df_runs', df_runs)
con.execute("INSERT INTO job_runs SELECT * FROM df_runs")

# load logs (optional)
if logs_dir and os.path.isdir(logs_dir):
    log_rows=[]
    for fname in os.listdir(logs_dir):
        if not fname.endswith('.txt'): continue
        jobname = fname.replace('_logs.txt','')
        with open(os.path.join(logs_dir,fname)) as f:
            log_rows.append((jobname, None, f.read()))
    if log_rows:
        df_logs=pd.DataFrame(log_rows, columns=['job','run_date','log'])
        con.register('df_logs', df_logs)
        con.execute("INSERT INTO job_logs SELECT * FROM df_logs")

print("Ingestion complete into", db)
con.close()

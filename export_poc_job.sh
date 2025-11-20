#!/bin/bash
# export_poc_job.sh
# Usage: ./export_poc_job.sh <JOB_NAME> <RUNS>
# e.g. ./export_poc_job.sh FLOW1_FINAL_JOB 30

JOB="$1"
RUNS="${2:-30}"
TS=$(date +%Y%m%d_%H%M%S)
OUTDIR="./export_${JOB}_${TS}"
mkdir -p "$OUTDIR/logs"

echo "[+] Exporting job definition and immediate condition lines..."
# job definition and condition (parents) - raw
autorep -j "$JOB" -q > "$OUTDIR/${JOB}_def.txt" 2>&1

echo "[+] Exporting run history (last $RUNS runs, basic)..."
autorep -j "$JOB" -r "$RUNS" > "$OUTDIR/${JOB}_run_history.txt" 2>&1

echo "[+] Exporting detailed run events (with eligible/start/end/queue) - last $RUNS..."
autorep -j "$JOB" -r "$RUNS" -d > "$OUTDIR/${JOB}_detailed.txt" 2>&1

echo "[+] Exporting stdout/stderr logs (last 10 runs)..."
autosyslog -J "$JOB" -n 10 > "$OUTDIR/logs/${JOB}_logs.txt" 2>&1

# Also export whole flow job list if naming convention exists (optional)
# Example: prefix=FLOW1_
# Uncomment and set if applicable:
# autorep -J "FLOW1_%" -s | awk '{print $1}' > "$OUTDIR/job_list.txt"

echo "[+] Done. Files in $OUTDIR"

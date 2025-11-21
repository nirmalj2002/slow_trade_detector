#!/bin/bash
# Usage: ./export_runs.sh deps_all.txt 30
# Export last N runs with -d details for every job in tree.

JOBLIST="$1"
RUNS="${2:-30}"

OUTDIR="runs_export_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTDIR"

echo "[+] Export directory: $OUTDIR"

while read JOB; do
    echo "[+] Exporting $RUNS runs for $JOB ..."
    autorep -j "$JOB" -r "$RUNS" -d > "$OUTDIR/${JOB}_runs.txt" 2>&1
done < "$JOBLIST"

echo "[+] Runs export complete."
echo "[+] Output in: $OUTDIR"

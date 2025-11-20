#!/usr/bin/env python3
# parse_runs.py
# Usage: python3 parse_runs.py <export_dir> <job> > runs.csv

import sys, re, os, pandas as pd
from datetime import datetime

export_dir = sys.argv[1]
job = sys.argv[2]
fpath = os.path.join(export_dir, f"{job}_detailed.txt")
text = open(fpath).read()

# autorep -d output is multiline per run. We'll find blocks with RUNID or "Event" lines.
runs = []
current = {}
for line in text.splitlines():
    line = line.strip()
    if not line:
        continue
    # Try patterns: "Event: STARTED    Event Time: 2025-11-20 12:34:56"
    m_evt = re.search(r"Event:\s*(\w+).*Event Time:\s*([0-9-]+ [0-9:]+)", line)
    if m_evt:
        evt = m_evt.group(1)
        tm = m_evt.group(2)
        # store by run occurrence grouping based on presence of RUNID or multiline - crude but practical
        runs.append((evt, tm))
# Fallback: attempt to parse lines with "Start Time" / "End Time" etc.
# More robust parsing:
pattern = re.compile(r"Start Time:\s*([0-9- :]+).*End Time:\s*([0-9- :]+).*Exit Status:\s*(\w+)", re.IGNORECASE)
# If pattern fails, try simpler scanning
if not pattern.search(text):
    # parse using common fields
    start_times = re.findall(r"Start Time:\s*([0-9- :]+)", text)
    end_times = re.findall(r"End Time:\s*([0-9- :]+)", text)
    statuses  = re.findall(r"Exit Status:\s*(\w+)", text)
    for i in range(min(len(start_times), len(end_times))):
        st = start_times[i]; et = end_times[i]
        try:
            sdt = datetime.strptime(st.strip(), "%Y-%m-%d %H:%M:%S")
            edt = datetime.strptime(et.strip(), "%Y-%m-%d %H:%M:%S")
            runs.append(("RUN", sdt.isoformat(), edt.isoformat()))
        except:
            pass
# Build dataframe
rows = []
for r in runs:
    if len(r) == 3:
        _, s, e = r
        rows.append({"job": job, "start_time": s, "end_time": e})
# If no structured runs found, warn and exit.
if not rows:
    print(f"# No runs parsed from {fpath}. Please verify autorep -d output format.", file=sys.stderr)
    sys.exit(1)

df = pd.DataFrame(rows)
df['start_time'] = pd.to_datetime(df['start_time'])
df['end_time']   = pd.to_datetime(df['end_time'])
df['duration_seconds'] = (df['end_time'] - df['start_time']).dt.total_seconds()
df.to_csv(sys.stdout, index=False)

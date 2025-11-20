#!/usr/bin/env python3
# analyze_dag.py
# Usage: python3 analyze_dag.py autosys_analysis.db <root_job> --window 30

import duckdb, networkx as nx, pandas as pd, sys, argparse
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('db')
parser.add_argument('root_job')
parser.add_argument('--baseline_runs', type=int, default=10)
args = parser.parse_args()

con = duckdb.connect(args.db)

# dependencies
deps_df = con.execute("SELECT job,parent FROM job_dependencies").df()
# job runs - use last baseline_runs for baseline then pick latest run for attribution
runs_df = con.execute("SELECT * FROM job_runs ORDER BY start_time DESC").df()

if runs_df.empty:
    print("No run data; ingest runs first.")
    sys.exit(1)

# Build graph (edges parent->job)
G = nx.DiGraph()
for _, row in deps_df.iterrows():
    G.add_edge(row['parent'], row['job'])

# Ensure root_job present, else include isolated node
if args.root_job not in G.nodes:
    G.add_node(args.root_job)

# compute baseline durations per job: avg of last N runs per job
baseline = runs_df.groupby('job').head(args.baseline_runs).groupby('job')['duration_seconds'].mean().to_dict()

# Latest run per job (the run that relates to current SLA evaluation)
latest = runs_df.groupby('job').first().reset_index().set_index('job')['duration_seconds'].to_dict()
latest_start = runs_df.groupby('job').first().reset_index().set_index('job')['start_time'].to_dict()
latest_end = runs_df.groupby('job').first().reset_index().set_index('job')['end_time'].to_dict()

# assign weights (use latest durations)
for n in G.nodes:
    G.nodes[n]['duration'] = latest.get(n, baseline.get(n, 0) or 0)

# compute longest path from any root ancestor to the final root_job.
# find all ancestors (sources)
sources = [n for n in G.nodes if G.in_degree(n)==0]
# try compute longest path to root_job
def path_weight(path):
    return sum(G.nodes[n].get('duration',0) for n in path)

best_path=None
best_weight= -1
for s in sources:
    if nx.has_path(G, s, args.root_job):
        p = nx.dag_longest_path(G.subgraph(nx.descendants(G, s)|{s,args.root_job}), weight='duration')
        w = path_weight(p)
        if w>best_weight:
            best_weight=w; best_path=p

print("Critical path to", args.root_job, ":", best_path)
print("Critical path total duration_seconds:", best_weight)

# Delay attribution: compare latest duration vs baseline
delay_scores = {}
for n in best_path:
    b = baseline.get(n, 0)
    l = latest.get(n, 0)
    delay_scores[n] = l - b

print("\nDelay contribution (latest - baseline):")
for n, d in sorted(delay_scores.items(), key=lambda x: -x[1]):
    print(f"{n:40} {d:.1f} sec (latest {latest.get(n,0):.1f}s, baseline {baseline.get(n,0):.1f}s)")

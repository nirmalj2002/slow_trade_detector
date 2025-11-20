#!/usr/bin/env python3
# parse_deps.py
# Usage: python3 parse_deps.py <export_dir> <root_job> > deps.json

import re, sys, json, os
from collections import defaultdict, deque

export_dir = sys.argv[1]
root_job = sys.argv[2]

# helper to read a job's def file (or run autorep directly if not found)
def read_def(job):
    path_guess = os.path.join(export_dir, f"{job}_def.txt")
    if os.path.exists(path_guess):
        return open(path_guess).read()
    # fallback: autorep -j job -q (requires CLI access)
    try:
        import subprocess
        out = subprocess.check_output(["autorep", "-j", job, "-q"], stderr=subprocess.STDOUT, text=True)
        return out
    except Exception as e:
        return ""

def extract_parents_from_text(text):
    parents = re.findall(r"s\(([^)]+)\)", text)  # s(jobX)
    parents += re.findall(r"f\(([^)]+)\)", text) # f(jobX) may be used for finished/other conds
    parents = [p.strip() for p in parents if p.strip()]
    return parents

# BFS to collect DAG around root_job
graph = defaultdict(list)
seen = set()
q = deque([root_job])
while q:
    job = q.popleft()
    if job in seen:
        continue
    seen.add(job)
    text = read_def(job)
    parents = extract_parents_from_text(text)
    graph[job] = parents
    for p in parents:
        if p not in seen:
            q.append(p)

print(json.dumps(graph, indent=2))

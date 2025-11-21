You are assisting in building a Shell-only Autosys Workflow Analysis Toolkit.

IMPORTANT:
- Everything must be done using shell (.sh), grep, sed, awk, and standard POSIX tools.
- No Python. No Perl. No external libraries.
- This toolkit will run on the Autosys AE server and must work with autorep/autosyslog CLI.
- The entire analytics pipeline must be implemented in shell scripts.

===========================================================
                 PROJECT GOALS (SHELL ONLY)
===========================================================

We want to analyze Autosys job flows and SLA delays with a full 
end-to-end pipeline built entirely in shell scripts.

The pipeline must:

1. Extract full multi-level dependency graph for a given job.
2. Export run history for all jobs in that dependency graph.
3. Parse Autosys detailed run output (-d) to extract:
       - start_time
       - end_time
       - eligible_time
       - wait_time (start - eligible)
       - duration_seconds
       - status
4. Compute baseline durations (average of last N runs per job).
5. Compute latest run durations.
6. Compute delay = latest - baseline.
7. Compute critical path for the entire job chain.
8. Identify which job contributed the most delay.
9. Produce a readable final report in plain text or CSV.
10. Everything must be done using Shell scripts, awk, sed, grep.

===========================================================
         FOLDER STRUCTURE (MANDATORY FOR ALL SCRIPTS)
===========================================================

After Step 1 (dependency crawl), we have this structure:

./deps_<JOB>/
    deps_all.txt      # 1 job per line
    deps_map.txt      # JOB: P1 P2 P3 ...
    deps_edges.txt    # PARENT CHILD (space-separated)

Step 1 script (crawl_dependencies.sh) is already implemented and working.
Do NOT modify Step 1.
All further scripts MUST use this structure.

After Step 2 (run export), we need this:

./runs_<JOB>_<TIMESTAMP>/
    JOB1_runs.txt
    JOB2_runs.txt
    JOB3_runs.txt
    ...

After Step 3 (optional logs):

./logs_<JOB>_<TIMESTAMP>/
    JOB1_logs.txt
    JOB2_logs.txt
    ...

After Step 4 (analysis output):

./analysis_<JOB>_<TIMESTAMP>/
    durations.csv
    baseline.csv
    delay.csv
    critical_path.txt
    report.txt

===========================================================
                 PHASE 1 — EXTRACTION (SHELL ONLY)
===========================================================

### STEP 1 — Dependency Crawl (already exists)
We already have this script:
    crawl_dependencies.sh <JOB>

It recursively calls autorep -j <job> -q and creates deps_<JOB> folder.
Do NOT regenerate or modify it.

### STEP 2 — Create export_runs.sh
This script must:

- Usage: ./export_runs.sh <deps_folder> <RUNS>
- Default RUNS=30
- Read jobs from <deps_folder>/deps_all.txt
- For each job:
      autorep -j <job> -r <RUNS> -d > runs_<timestamp>/<job>_runs.txt
- Create output folder:
      runs_<ROOT_JOB>_YYYYMMDD_HHMMSS/
- Skip blank lines
- Handle missing jobs gracefully
- Print progress
- Must not overwrite old export directories (always timestamp)

### STEP 3 — Create export_logs.sh (optional)
- Usage: ./export_logs.sh <deps_folder> [NUM_LOGS]
- Default NUM_LOGS=5
- Call:
      autosyslog -J <job> -n <NUM_LOGS>
- Output folder:
      logs_<ROOT_JOB>_<TIMESTAMP>/

===========================================================
                PHASE 2 — ANALYSIS (SHELL ONLY)
===========================================================

All analysis must be done in *pure shell / awk / sed*.

### STEP 4 — Create parse_runs.sh
Objective:
For each *_runs.txt file:
- Extract:
    job_name
    run_id  (if present or inferable)
    start_time
    end_time
    eligible_time  (if present)
    wait_time = start_time - eligible_time
    duration_seconds = (end - start)
    status
- Handle Autosys 11.x/12.x formats.
- Produce a CSV with columns:
    job,run_id,start_time,end_time,eligible_time,wait_time,duration_seconds,status

Output:
    parsed_runs.csv

### STEP 5 — Create build_runtime_tables.sh
Compute baseline averages and latest-run durations.

Inputs:
- parsed_runs.csv

Outputs:
- baseline.csv         (job, baseline_duration)
- latest.csv           (job, latest_duration)
- delay.csv            (job, delay_seconds)

Delay = latest - baseline.

### STEP 6 — Create compute_critical_path.sh
Using deps_edges.txt and latest durations:

- Construct DAG in shell/awk.
- Compute longest (duration-weighted) path from root to target job.
- Output:
      critical_path.txt
      critical_path_duration.txt

### STEP 7 — Create delay_attribution.sh
- Identify delay contribution for each job on the critical path.
- Output sorted delay contributions.

Example output:
    JOB_E  +420
    JOB_B  +35
    JOB_A  +12

### STEP 8 — Create final_report.sh
Generate a human-readable report combining:

- Critical path
- Path total durations
- Baseline vs latest
- Delay attribution
- Summary sections

Output:
    analysis_<JOB>_<TIMESTAMP>/report.txt

===========================================================
                      RULES FOR COPILOT
===========================================================

- All scripts must be pure POSIX shell. No Python.
- Use awk extensively for table operations and timestamp math.
- Every script must validate input arguments.
- Every script must show clear logging (echo statements).
- Never overwrite previous outputs; use timestamped folders.
- Be robust to unexpected whitespace and missing fields.
- Producing sorted, readable results is required.
- Scripts must gracefully handle very large dependency graphs.

===========================================================
                     DELIVERABLES LIST
===========================================================

Generate the following scripts (one by one when asked):

1. export_runs.sh
2. export_logs.sh
3. parse_runs.sh
4. build_runtime_tables.sh
5. compute_critical_path.sh
6. delay_attribution.sh
7. final_report.sh
8. README.md (shell-only version)

Do NOT generate all scripts at once unless instructed.
Start with individual scripts upon request.

Acknowledge this prompt when ready.

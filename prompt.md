You are assisting in building a Shell-only Autosys Data Extraction Toolkit. 
The goal is to extract all required data from Autosys AE using autorep and autosyslog, 
and store it in a structured folder so that downstream Python analytics can run locally.

You must generate POSIX-compliant, durable .sh scripts. No Python, no awk tricks that vary by OS. 
Use grep, sed, awk, and bash only. All scripts must handle:
- multi-level dependencies,
- jobs with multiple parents,
- deep recursion,
- missing condition lines,
- large dependency trees.

## PROJECT REQUIREMENTS

We have a two-step export workflow:

### STEP 1 — Dependency Extraction
We already have a working script named: `crawl_dependencies.sh`
This script produces a folder with the following files:

./deps_<JOB>/
    deps_all.txt      # All jobs recursively found in the dependency DAG
    deps_map.txt      # JOB: parent1 parent2 ...
    deps_edges.txt    # parent child pairs, space-separated

Do NOT modify Step 1; only use its output.

### STEP 2 — Run History Export
We need a shell script that:
1. Reads deps_all.txt from Step 1
2. Exports run history for each job using:
      autorep -j <job> -r <N> -d
3. Stores each file under:
      runs_<JOB>_<timestamp>/<job>_runs.txt
4. Handles missing jobs or errors gracefully
5. Offers configurable number of runs (default 30)

### STEP 3 — (Optional) Log Export
We may later add a script to extract last N logs via:
      autosyslog -J <job> -n 5
These logs should be placed under:
      logs_<JOB>_<timestamp>/<job>_logs.txt

For now, only generate Step 2 unless asked.

## SCRIPT EXPECTATIONS

- Always create output directories safely (mkdir -p).
- Never overwrite existing files silently; use timestamps.
- Add clear logging/echo statements for observability.
- Validate input arguments (job name, deps folder exists, etc.).
- Validate presence of deps_all.txt and exit with meaningful errors.
- Make scripts work even if the dependency tree has 200+ jobs.
- Handle unexpected blank lines in deps_all.txt.

## DELIVERABLE

Produce a clean, documented shell script named:
     export_runs.sh

The script must:
- Accept arguments: <deps_folder> <RUNS>
- Default RUNS=30
- Export run histories for every job listed in deps_all.txt
- Save them under a timestamped folder like:
      runs_export_YYYYMMDD_HHMMSS/
- Print summary at the end.

Do NOT include analysis code; only export logic.

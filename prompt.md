You are helping build an end-to-end Autosys Analytics Toolkit.

IMPORTANT ARCHITECTURE REQUIREMENT:
-----------------------------------
PHASE 1 (Autosys AE server): 
    - Shell-only (.sh). No Python. No pip. 
    - Uses autorep, autosyslog commands.
    - Extract raw data only.

PHASE 2 (Local machine): 
    - Python-only. 
    - Performs DAG building, critical path analysis, delay attribution, visualization.

Your job is to generate ALL scripts for both PHASE 1 and PHASE 2.
Be strictly aware of dependencies and folder structure.

================================================================
 PHASE 1 — AUTOSYS SERVER (Shell-only)
================================================================

GOAL:
Extract all required raw data from Autosys AE for ONE JOB FLOW:
1. Recursive dependency graph (parents, grandparents, multi-level DAG)
2. Run history (start/end/duration/eligible/queue)
3. (Optional) Logs

No Python on Autosys server. Only shell + Autosys CLI.

FOLDER STRUCTURE (MANDATORY):
-----------------------------
After running Step 1 (dependency crawler), we have:

./deps_<JOB>/
    deps_all.txt      # List of all jobs in dependency graph (1 per line)
    deps_map.txt      # JOB: P1 P2 ...
    deps_edges.txt    # PARENT CHILD

We must NOT modify Step 1 results.
Step 2 must READ deps_all.txt exactly as is.

### STEP 1: Dependency crawl (already working)
We already have:
    crawl_dependencies.sh <ROOT_JOB>
that produces deps_<JOB>/ folder above.
Do not modify this script.
Only use its output.

### STEP 2: Export run history (required)
Generate a shell script named:
    export_runs.sh

Requirements:
- Usage: ./export_runs.sh <deps_folder> <RUNS>
- Default RUNS=30
- Read jobs from: <deps_folder>/deps_all.txt
- For each job:
     autorep -j <job> -r <RUNS> -d > runs_<timestamp>/<job>_runs.txt
- Create timestamped output folder like:
     runs_<ROOT_JOB>_YYYYMMDD_HHMMSS/
- Skip blank lines safely
- Log progress
- Handle missing job definitions gracefully

### STEP 3: Export logs (optional)
Generate a script named:
    export_logs.sh

Requirements:
- Usage: ./export_logs.sh <deps_folder> [NUM_LOGS]
- Default NUM_LOGS=5
- For each job in deps_all.txt:
     autosyslog -J <job> -n <NUM_LOGS> > logs_<timestamp>/<job>_logs.txt
- Create timestamped folder:
     logs_<ROOT_JOB>_YYYYMMDD_HHMMSS/
- Logs are optional enrichment for root-cause analysis.

### STEP 4: Packaging
Generate a script named:
    package_export.sh

Requirements:
- Should zip:
    deps_<JOB>/
    runs_<TIMESTAMP>/
    logs_<TIMESTAMP>/  (if exists)
- Name ZIP as:
    autosys_export_<JOB>_<TIMESTAMP>.zip

================================================================
 PHASE 2 — LOCAL MACHINE (Python analysis)
================================================================

Once the ZIP is downloaded locally, we run Python on laptop.

You must generate the following Python modules:

### A) parse_runs.py
Input: runs_<timestamp>/*_runs.txt  
Output: pandas DataFrame with:

job  
run_id (extract if possible)  
start_time  
end_time  
duration_seconds  
eligible_time (from autorep -d event lines)  
wait_time = start_time - eligible_time  
status  

Must handle Autosys 12.x format (“Event: STARTED”, “Event Time:” etc.).  
Include defensive regex parsing.

### B) build_dag.py
Input: deps_edges.txt  
Output: NetworkX DiGraph  
Edges: parent → child  
Identify root nodes (no incoming edges).  
Identify final job (highest child).

### C) critical_path.py
Requirement:
- Compute longest-duration path in DAG.
- Use run durations from parsed DataFrame.
- Support selecting critical path for a specific run date.
- Output list of jobs + total duration.

### D) delay_attribution.py
Compute:
    baseline_duration = average of last N runs per job
    latest_duration   = most recent run
    delay = latest - baseline

Produce sorted table:
    job | baseline | latest | delay_seconds

### E) main or notebook
Provide a script or notebook demonstrating:

1. Load deps_edges.txt  
2. Load parsed run history  
3. Build DAG  
4. Compute critical path  
5. Compute delay attribution  
6. Print report  
7. (Optional) Visualize DAG and Gantt chart

### Python environment assumptions:
- Python 3.10+
- pandas
- networkx
- matplotlib (optional)
All available locally.

================================================================
 GENERAL RULES
================================================================

- All scripts must be clean, documented, production-ready.
- Shell scripts must use safe practices: set -e, set -u optional.
- Python scripts must handle unexpected formatting in autorep output.
- Preserve folder structure between PHASE 1 and PHASE 2.
- Use descriptive variable names.
- Always print helpful progress/log messages.

================================================================
 DELIVERABLES
================================================================

1. export_runs.sh
2. export_logs.sh
3. package_export.sh
4. parse_runs.py
5. build_dag.py
6. critical_path.py
7. delay_attribution.py
8. Example main.py or notebook
9. README.md describing full workflow

Generate code only when asked; for now, acknowledge the prompt.

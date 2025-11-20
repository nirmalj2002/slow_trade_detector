6) Example SQL snippets you can run from DuckDB console

Top slowest jobs overall:

SELECT job, AVG(duration_seconds) avg_dur, COUNT(*) runs
FROM job_runs
GROUP BY job
ORDER BY avg_dur DESC
LIMIT 50;


Last run durations:

SELECT job, duration_seconds, start_time, end_time
FROM job_runs
QUALIFY ROW_NUMBER() OVER (PARTITION BY job ORDER BY start_time DESC)=1
ORDER BY start_time DESC;


Dependencies:

SELECT * FROM job_dependencies;

7) Schedule automated export (cron)

Create a small wrapper to run export + parse + ingest nightly. Example crontab entry (runs at 01:15 AM):

15 1 * * * /opt/tools/export_and_ingest_poc.sh >> /var/log/autosys_poc_export.log 2>&1


export_and_ingest_poc.sh should call in sequence:

export_poc_job.sh JOB RUNS

python3 parse_deps.py ...

python3 parse_runs.py ...

python3 ingest_to_duckdb.py ...

python3 analyze_dag.py ...

Make sure to set full paths and environment for autorep and autosyslog (source any profile if needed).

8) Quick testing checklist (POC)

Run ./export_poc_job.sh <JOB> 30 — confirm files created.

Run python3 parse_deps.py ./export_<JOB>_<TS> <JOB> > deps.json — inspect deps.json.

Run python3 parse_runs.py ./export_<JOB>_<TS> <JOB> > runs.csv — open CSV to verify timestamps.

Run python3 ingest_to_duckdb.py autosys_analysis.db deps.json runs.csv <export_dir>/logs

Run python3 analyze_dag.py autosys_analysis.db <JOB> — check outputs.

If a parser fails because your autorep -d formatting is slightly different, paste a small snippet of detailed.txt and I’ll refine the regexes (I’ve built the parser to be defensive but every Autosys flavor can differ across versions/install options).
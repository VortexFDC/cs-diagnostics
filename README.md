# cs-diagnostics
Repo with useful functions to asses differences between skeleton versions
Also includes code to submit validation batch.
Note: Need to create code to get work_id from run_id (also to set runs to branch)

## Scripts:
- `get.works.sh`:
    Bash script to download run results from the server.
    It requires:
    - `mshop_runs.csv`: File containing the `run_id` and `work_id` of the runs we want to analyze
- `compare.py`: Python module with functions to load run results and compare them
- `do.compare.py`: Basic python script to compare if two runs have produced the same time series (for essential variables only)
- `submit.validation.py`: Python script to submit validation runs for sites and maps.
    It requires:
    - `val.maps.csv` and `val.sites.csv`: Lists of locations to be included in validation
    Produces:
    - `submitted_\{product\}s_\{version_prefix\}_\{source\}.csv` files with run_ids of the submitted runs.


# Next steps
- Allow for comparison of derived variables 
# cs-diagnostics
Repo with useful functions to asses differences between skeleton versions
Also includes code to submit validation batch.
Note: Need to create code to get work_id from run_id (also to set runs to branch)

## Scripts:

### Helpers:
- `get.works.sh`:
    Bash script to download run results from the server.
    It requires:
    - `works.csv`: File containing the `run_id` and `work_id` of the runs we want to download.
- `compare.py`: Python module with functions to load run results and compare them.
- `ddbb.py`: Python module to connect and query the database.

### Mains:
- `submit.validation.py`: Python script to submit validation runs for sites and maps.
    It requires:
    - `val.maps.csv` and `val.sites.csv`: Lists of locations to be included in validation
    Produces:
    - `submitted_{product}s_{version_prefix}_{source}.csv` files with run_ids of the submitted runs.
- `version_compare.py`: Script to download run results and perform full version comparison.
  - To be run after version runs finish.
  - It connects to DDBB to extract work ids for the submitted runs and uses `get.works.sh` to download the data. (Uses submitted_*.csv files)
  - Provides MAE between versions for all variables, scenarios and stages.

# Next steps
- Allow for comparison of derived variables 
- Request reports for submitted sites
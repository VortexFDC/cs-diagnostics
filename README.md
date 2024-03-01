# cs-diagnostics
Repo with usefull functions to asses differences between skeleton versions

## Scripts:
- get.works.sh:
    Bash script to download run results from the server.
    It requires:
    - `mshop_runs.csv`: File containing the `run_id` and `work_id` of the runs we want to analyze
    - `compare.py`: Python module with functions to load run results and compare them
    - `do.compare.py`: Basic python script to campare if two runs have produced the same time series (for essential variables only)

# Next steps
- Allow for comparison of derived variables 
import os
import pandas as pd
from ddbb import get_run_work_desc
import subprocess
import compare

def load_version_runs(product, source, versions):
    dfs = []
    for version_prefix in versions:
        df_runs = pd.read_csv(f"submitted_sites_{version_prefix}_{source}.csv")
        df = get_run_work_desc(source, product, df_runs["run_id"].values)
        df[["run_version", "site_name"]] = df["run_desc"].str.split("-", expand=True)
        dfs.append(df)
    df = pd.concat(dfs)
    df = df.drop(columns=["run_desc"]).pivot_table(index="site_name", columns="run_version")
    return df

### Compare two versions of a product and source
# Set up product and source to analyze
product = "site"
source = "cmip6"
# Versions to compare
versions = ["v1", "v2"]

# Load version runs
df_versions = load_version_runs(product, source, versions)

## TEMP - Limit to 5 runs
#df_versions = df_versions.head(5)

# Download works
for version in versions:
    print(f"Getting runs for version {version} ... ")
    df_versions.loc[:,[('run_id',version.upper()), ('wrk_id',version.upper())]].to_csv("works.csv",header=False, index=False)
    subprocess.run(["./get.works.sh >> download.log"], shell=True)


# Compare works
results = {}
for name in df_versions.index:
    print(f"Comparing {name} ...")
    res = compare.compare_two_works(*df_versions.loc[name,("wrk_id")].tolist())
    if res == {}:
        print(f"No differences found for {name}.")
        continue
    results[name] = res


# Check results
print()
print("Results:")
# Find sites with differences
site_diffs = [ name for name in results.keys() ]
if len(site_diffs) == 0:
    print("No differences found.")
    exit()

print(f"Differences found in sites {len(site_diffs)/len(df_versions.index)*100:.2f} % of sites.")
    
# Find stages with differences
stage_diffs = []
if any([ "obs" in results[name] for name in results.keys() ]):
    stage_diffs.append("obs")

if any([ "ext" in results[name] for name in results.keys() ]):
    stage_diffs.append("ext")

if any([ "new" in results[name] for name in results.keys() ]):
    stage_diffs.append("new")

print("Differences found in stages: ", stage_diffs)
if len(stage_diffs) == 0:
    print("No differences found.")
    exit()

# Create dataframe
# Delete columns with all 0s
df_results = {}
for stage in stage_diffs:
    if stage == "obs":
        df = pd.concat({ name : results[name]["obs"]["mae"] for name in results.keys() if "obs" in results[name] }, axis=1).T
        df.index.names = ["site"]
    elif stage == "ext":
        df = pd.concat({ name : pd.concat( { scen : results[name]["ext"][scen]["mae"] for scen in results[name]["ext"].keys() } ) for name in results.keys() if "ext" in results[name].keys()})
        df.index.names = ["site", "scen", "model"]
    elif stage == "new":
        df = pd.concat({ name : pd.concat( { scen : results[name]["new"][scen]["mae"] for scen in results[name]["new"].keys() } ) for name in results.keys() if "new" in results[name].keys()})
        df.index.names = ["site", "scen", "model"]
    df = df.loc[:, (df != 0).any(axis=0)]
    df_results[stage] = df
    # Save to csv
    df.to_csv(f"results_compare-{'-'.join(versions)}_{stage}.csv")



### Plot results
import matplotlib.pyplot as plt

variables = None
for stage in stage_diffs:
    if stage == "obs":
        if variables is None:
            variables = df_results[stage].columns
        df_results[stage].reset_index().boxplot(column=variables, vert=False)
    else:
        if variables is None:
            variables = df_results[stage].columns
        df_results[stage].reset_index().boxplot(column=variables, by=["scen"], vert=False)
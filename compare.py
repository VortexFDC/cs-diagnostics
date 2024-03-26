import xarray as xr
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
#import matplotlib.pyplot as plt
import os


"""
This module contains functions to load and compare time series data from two different work directories.
"""

def get_list_of_models_and_scenarios(path):
    """Get list of models and scenarios from the data directory."""
    models = []
    scenarios = []
    for root, dirs, files in os.walk(path):
        if "extend" in root:
            for file in files:
                if file.startswith("cmip"):
                    models.append(file.split(".")[3])
                    scenarios.append(file.split(".")[2])
        if "new" in root:
            for file in files:
                if file.startswith("cs5"):
                    models.append(file.split(".")[2])
                    scenarios.append(file.split(".")[1])
    return list(set(models)), list(set(scenarios))

def get_data_variable(ds):
    return [ var for var in list(ds.variables) if var not in list(ds.coords)]

def load_ts(wrk, var, mdl=None, scen=None, stage="extend", rename=False):
    """
    Load time series data from the work directory at a given stage.
    Only essentai variables are loaded.
    Args:
    wrk: (str) Name of the work directory.
    var: (str) Name of the variable.
    mdl: (str) Name of the model.
    scen: (str) Name of the scenario.
    stage: (str) Sage of the data (extend, new, obs).
            obs stage will look for the recalibrated data first.
    """
    if stage == "extend":
        file_var = "x"
        fn = f"data/{wrk}/out/ts/extend/cmip6.extend.{scen}.{mdl}.{var}.da.ab.nc"
    elif stage == "new":
        file_var = "var"
        fn = f"data/{wrk}/out/new/essential/cs5.{scen}.{mdl}.{var}.da.ab.nc"
    elif stage == "obs":
        file_var = "y"
        fnrecal = f"data/{wrk}/out/ts/obs/era5.{var}.recal.da.ab.nc"
        if os.path.exists(fnrecal):
            fn = fnrecal
        else:
            fn = f"data/{wrk}/out/ts/obs/era5.{var}.da.ab.nc"
    
    
    if not os.path.exists(fn):
        raise FileNotFoundError(f"File {fn} not found.")
    ds = xr.open_dataset(fn)
    if rename:
        ds = ds.rename({file_var:var})
    return ds
    
def load_all_models(wrk, var, scen, stage="extend", rename=False, floor=True):
    """
    Load time series data from the work directory at a given stage for all models.
    Args:
    wrk: (str) Name of the work directory.
    var: (str) Name of the variable.
    scen: (str) Name of the scenario.
    stage: (str) Sage of the data (extend, new, obs).
    """
    ds = {}
    if stage == "obs":
        ds["ERA5"] = load_ts(wrk, var, stage=stage, rename=rename)
    else:
        for mdl in MODELS:
            try: ds[mdl] = load_ts(wrk, var, mdl, scen, stage=stage, rename=rename)
            except: continue
            if floor:
                ds[mdl]["time"] = ds[mdl]["time"].dt.floor("D")
    return xr.concat(ds.values(), dim=pd.Index(ds.keys(), name="model"))

def load_all_models_and_scenarios(wrk, var, stage="extend", rename=False, floor=True):
    ### Is better to do this as a dict of datasets with the scenario as the key
    """
    Load time series data from the work directory at a given stage for all models and scenarios.
    Args:
    wrk: (str) Name of the work directory.
    var: (str) Name of the variable.
    stage: (str) Sage of the data (extend, new, obs).
    """
    ds = {}
    for scen in SCENARIOS:
        try: ds[scen] = load_all_models(wrk, var, scen, stage=stage, rename=rename, floor=floor)
        except: continue
    return xr.concat(ds.values(), dim=pd.Index(ds.keys(), name="scenario"))

def load_variables(wrk, variables, scen=None, stage="extend", rename=True, floor=True):
    """
    Load time series data from the work directory at a given stage for all models.
    Args:
    wrk: (str) Name of the work directory.
    variables: (list) List of variable names.
    scen: (str) Name of the scenario.
    stage: (str) Sage of the data (extend, new, obs).
    """
    ds = []
    for var in variables:
        try: ds.append(load_all_models(wrk, var, scen, stage=stage, rename=rename, floor=floor))
        except: continue
    return xr.merge(ds)[variables]

# Metrics to compute
# - Mean absolute error
# - Kolmogorov-Smirnov test

def compute_mae(ds1, ds2):
    """
    Compute the mean absolute error between two datasets over time.
    """
    return (ds2 - ds1).apply(np.fabs).mean("time").to_pandas().drop(columns=["lat","lon"])

def compute_ks(ds1, ds2, return_pvalues=False):
    """
    Compute the Kolmogorov-Smirnov test between two datasets over time.
    """
    results = {}
    presults = {}
    for var in get_data_variable(ds1):
        results[var] = {}
        presults[var] = {}
        for mdl in ds1.model.values:
            ds1_sel = ds1[var].sel({"model":mdl}).values
            ds2_sel = ds2[var].sel({"model":mdl}).values
            if np.isnan(ds1_sel).all() or np.isnan(ds2_sel).all():
                ks,pval = np.nan,np.nan
            else:
                ks,pval = ks_2samp(ds1[var].sel({"model":mdl}).values, ds2[var].sel({"model":mdl}).values)
            results[var][mdl] = ks
            presults[var][mdl] = pval
    if return_pvalues:
        return pd.DataFrame(results), pd.DataFrame(presults)
    return pd.DataFrame(results)


MODELS, SCENARIOS = get_list_of_models_and_scenarios("data")
VARIABLES = ["tas","tasmin","tasmax","pr","wind10","wind100","rhum","rsds"]

def compare_two_works(work_1, work_2):
    """
    Compare two works and return a dictionary with the results.
    """
    models_1, scenarios_1 = get_list_of_models_and_scenarios(f"data/{work_1}")
    models_2, scenarios_2 = get_list_of_models_and_scenarios(f"data/{work_2}")

    print("Check if the models and scenarios are the same...")
    if models_1 != models_2:
        raise ValueError("Runs do not have same models.")
    if scenarios_1 != scenarios_2:
        raise ValueError("Runs do not have same scenarios.")
    if models_1 == models_2 and scenarios_1 == scenarios_2:
        print("Models and scenarios are the same.")

    results = {'obs': {}, 'ext': {}, 'new': {}}

    # Load obs data
    ds_1_obs = load_variables(work_1, VARIABLES, stage="obs").squeeze()
    ds_2_obs = load_variables(work_2, VARIABLES, stage="obs").squeeze()

    print("### - CHECKING OBS - ###")
    mae = compute_mae(ds_1_obs, ds_2_obs)
    if not (mae.isna() | (mae == 0)).all().all():
        results["obs"]["mae"] = mae
    else:
        print("No differences found.")
    
    # Load model data
    ds_1_ext = { scen: load_variables(work_1, VARIABLES, scen, "extend").squeeze() for scen in SCENARIOS }
    ds_2_ext = { scen: load_variables(work_2, VARIABLES, scen, "extend").squeeze() for scen in SCENARIOS }
    ds_1_new = { scen: load_variables(work_1, VARIABLES, scen, "new").squeeze() for scen in SCENARIOS }
    ds_2_new = { scen: load_variables(work_2, VARIABLES, scen, "new").squeeze() for scen in SCENARIOS }

    for scen in SCENARIOS:
        print(f"### - CHECKING EXT {scen} - ###")
        results["ext"][scen] = {}
        mae = compute_mae(ds_1_ext[scen], ds_2_ext[scen])
        if not (mae.isna() | (mae == 0)).all().all():
            results["ext"][scen]["mae"] = mae
        else:
            print("No differences found.")
        
        print(f"### - CHECKING NEW {scen} - ###")
        results["new"][scen] = {}
        mae = compute_mae(ds_1_new[scen], ds_2_new[scen])
        if not (mae.isna() | (mae == 0)).all().all():
            results["new"][scen]["mae"] = mae
        else:
            print("No differences found.")

    if results_is_empty(results):
        return {}
    else:
        return prune_results(results)

def results_is_empty(results):
    obs_is_empty = results["obs"] == {}
    ext_is_empty = all([results["ext"][scen] == {} for scen in SCENARIOS])
    new_is_empty = all([results["new"][scen] == {} for scen in SCENARIOS])
    if obs_is_empty and ext_is_empty and new_is_empty:
        return True
    return False

def prune_results(results):
    """
    Prune results with no differences.
    """
    results_pruned = {}
    if results["obs"] != {}:
        results_pruned["obs"] = results["obs"]
    if results["ext"] != { scen: {} for scen in SCENARIOS }:
        results_pruned["ext"] = { scen: results["ext"][scen] for scen in SCENARIOS if results["ext"][scen] != {} }
    if results["new"] != { scen: {} for scen in SCENARIOS }:
        results_pruned["new"] = { scen: results["new"][scen] for scen in SCENARIOS if results["new"][scen] != {} }
    return results_pruned
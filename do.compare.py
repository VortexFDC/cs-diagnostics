import compare

#work_1 = 9873
work_1 = 10051
work_2 = 10049

models_1, scenarios_1 = compare.get_list_of_models_and_scenarios(f"data/{work_1}")
models_2, scenarios_2 = compare.get_list_of_models_and_scenarios(f"data/{work_2}")

print("Check if the models and scenarios are the same...")
if models_1 != models_2:
    raise ValueError("Runs do not have same models.")
if scenarios_1 != scenarios_2:
    raise ValueError("Runs do not have same scenarios.")
if models_1 == models_2 and scenarios_1 == scenarios_2:
    print("Models and scenarios are the same.")

# Load obs data
ds_1_obs = compare.load_variables(work_1, compare.VARIABLES, stage="obs").squeeze()
ds_2_obs = compare.load_variables(work_2, compare.VARIABLES, stage="obs").squeeze()

print("### - CHECKING OBS - ###")
obs_mae = compare.compute_mae(ds_1_obs, ds_2_obs)
if not (obs_mae.isna() | (obs_mae == 0)).all().all():
    print(obs_mae)
else:
    print("No differences found.")

# Load model data
ds_1_ext = { scen: compare.load_variables(work_1, compare.VARIABLES, scen, "extend").squeeze() for scen in compare.SCENARIOS }
ds_2_ext = { scen: compare.load_variables(work_2, compare.VARIABLES, scen, "extend").squeeze() for scen in compare.SCENARIOS }
ds_1_new = { scen: compare.load_variables(work_1, compare.VARIABLES, scen, "new").squeeze() for scen in compare.SCENARIOS }
ds_2_new = { scen: compare.load_variables(work_2, compare.VARIABLES, scen, "new").squeeze() for scen in compare.SCENARIOS }

for scen in compare.SCENARIOS:
    print()
    print(f"### - CHECKING {scen} - ###")
    print("### EXT ")
    ext_mae = compare.compute_mae(ds_1_ext[scen], ds_2_ext[scen])
    if not (ext_mae.isna() | (ext_mae == 0)).all().all():
        print(ext_mae)
    else:
        print("No differences found.")
    
    print("### NEW ")
    new_mae = compare.compute_mae(ds_1_new[scen], ds_2_new[scen])
    if not (new_mae.isna() | (new_mae == 0)).all().all():
        print(new_mae)
    else:
        print("No differences found.")
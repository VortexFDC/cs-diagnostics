from CSUtils.API import API
import pandas as pd
import os

version_prefix = "v2"
sources = ["cmip5", "cmip6"]

# Login to the API as validations user
url = "https://api.climatescale.com"
user = "validations@climatescale.com"
password = "ValUser23"

api = API(url, user, password)

# Submit validation runs
# Include all products (not series)
# Include all CMIP5 & CMIP6
# Include onshore & offshore
# Include all technologies

# Point locations
df_points = pd.read_csv("val.sites.csv")
df_points["name"] = version_prefix +"-"+ df_points["name"]
df_points.to_csv("foo.sites.csv", index=False, header=False)

# Submit sites
for source in sources:
    df0, df1 = api.submit_sites(source=source, fn="foo.sites.csv", silence=True)
    df0.rename(columns={0:"name",1:"run_id"})[["name","run_id"]].to_csv(f"submitted_sites_{version_prefix}_{source}.csv", index=False)
    if df1.empty:
        print("Sites submitted successfully")

## Submits maps
#df_maps = pd.read_csv("val.maps.csv")
#df_maps["name"] = version_prefix +"-"+ df_maps["name"]
#df_maps.to_csv("foo.smaps.csv", index=False, header=False)
#
## Submit smaps
#for source in sources:
#    df0, df1 = api.submit_smaps(source=source, fn="foo.smaps.csv", silence=True)
#    df0.rename(columns={0:"name",1:"run_id"})[["name","run_id"]].to_csv(f"submitted_smpas_{version_prefix}_{source}.csv", index=False)
#    if df1.empty:
#        print("Maps submitted successfully")

# Remove foo.csv files 
os.remove("foo.sites.csv")
#os.remove("foo.smaps.csv")

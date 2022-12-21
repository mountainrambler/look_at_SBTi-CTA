"""
Created on Wed Dec 21 16:07:09 2022

@author: peter.nystrom
"""

import requests
import pandas as pd

CTA_URL = "https://sciencebasedtargets.org/download/excel"

resp = requests.get(CTA_URL)
cta_file = resp.content
if not resp.status_code == 200:
    print("Something went wrong when fetching the file, try again later")
else:
    print("File ok")
    
cta_df = pd.read_excel(cta_file)

cta_swe = cta_df.loc[cta_df['Location'] == 'Sweden'] 

# Get some numbers
# Total number of companies
tot_companies = cta_df.shape[0]
tot_swe = cta_swe.shape[0]

# Data on near term (nt) targets
tot_valid_nt = cta_df.loc[cta_df['Near term - Target Status'] == 'Targets Set'].shape[0]
swe_valid_nt = cta_swe.loc[cta_swe['Near term - Target Status'] == 'Targets Set'].shape[0]
# committed companies
tot_commit = tot_companies - tot_valid_nt
swe_commit = tot_swe - swe_valid_nt
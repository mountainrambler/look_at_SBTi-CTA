"""
Module for interacting with the Science Based Targets Initiative (SBTi) database.

The Science Based Targets Initiative (SBTi) is a collaboration between CDP, the United Nations Global Compact, World Resources Institute (WRI) and the World Wide Fund for Nature (WWF). The initiative aims to provide companies with a clear pathway to set and achieve science-based emissions reduction targets.

The CTA class can be used to download and manipulate data from the SBTi database.

Attributes:
CTA_URL (str): URL for downloading the SBTi database in Excel format.

Classes:
CTA: Class for interacting with the SBTi database.

"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from tabulate import tabulate 

CTA_URL = "https://sciencebasedtargets.org/download/excel"

class CTA:
    def __init__(self, url):
        self.url = url
        self.data = pd.DataFrame()
        self.swe = None
        self.tot_companies = None
        self.tot_swe = None
        self.tot_valid_nt = None
        self.swe_valid_nt = None
        self.tot_commit = None
        self.swe_commit = None

    def get_data(self):
        resp = requests.get(self.url)
        cta_file = resp.content
        if not resp.status_code == 200:
            print("Something went wrong when fetching the file, try again later")
        else:
            print("File ok")
        self.data = pd.read_excel(cta_file)
        self.data.dropna(subset='Date', inplace=True)
        self.data['Date'] = self.data['Date'].astype('str')
        self.data['Date'] = self.data['Date'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y'))

        #return self.data

    def run_SBTi(self):
        pd = self.get_data()
        self.prepare_data(pd)
    

    def prepare_data(self):

        filt = self.data['Location'] == 'Sweden'
        self.tot_swe = self.data.loc[filt] 

        # Get some numbers
        # Total number of companies
        num_tot_companies = self.data.shape[0]
        num_tot_swe = self.tot_swe.shape[0]

        # Data on near term (nt) targets
        self.tot_valid_nt = self.data.loc[self.data['Near term - Target Status'] == 'Targets Set'].copy()
        self.swe_valid_nt = self.tot_swe.loc[self.tot_swe['Near term - Target Status'] == 'Targets Set'].copy()
        # committed companies
        self.tot_commit = num_tot_companies - self.tot_valid_nt.count()
        self.swe_commit = num_tot_swe - self.swe_valid_nt.count()

        df_swe= self.tot_swe[['Company Name', 'Date']].copy()
        df_swe_valid = self.swe_valid_nt[['Company Name', 'Date']].copy()
        
        # Populate data table
        table = [['CTA', 'Tot Companies', 'Tot Swe', 'Tot Valid', 'Tot Swe Valid'],
                 ['num', num_tot_companies, num_tot_swe, self.tot_valid_nt.shape[0], self.swe_valid_nt.shape[0]],
                 ['% of total', '-',f'{int(100*num_tot_swe/num_tot_companies)}%', 12, 12 ]]
        self.print_data_table(table)
        self.plot_num_companies_per_year(df_swe, "Total", "Sweden")
        self.plot_num_companies_per_year(df_swe_valid, "Validated", "Sweden")


    def plot_num_companies_per_year(self, df, status, geo):
        # Create a new column with the year of registration
        df['year'] = df['Date'].dt.year

        # Group by year and count the number of companies
        year_counts = df.groupby('year')['Company Name'].count()
        ax = year_counts.plot.bar()
        
        # Add the value on top of each bar
        for p in ax.patches:
            ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))
        # Plot the year counts as a bar chart
        # year_counts.plot.bar()
        plt.xlabel('Year')
        plt.ylabel('Number of Companies')
        plt.title(f'({geo})Number of Companies {status} per Year, total is {year_counts.sum()}')

        plt.show()
        
    def print_data_table(self, table):
        print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))
        
        
        
cta = CTA(CTA_URL)
cta.get_data()
cta.prepare_data()
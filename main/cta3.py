import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

CTA_URL = "https://sciencebasedtargets.org/download/excel"

def get_file(url: str) -> pd.DataFrame:
    resp = requests.get(url)
    cta_file = resp.content
    if not resp.status_code == 200:
        print("Something went wrong when fetching the file, try again later")
    else:
        print("File ok")

    data = pd.read_excel(cta_file)
    data.dropna(subset='Date', inplace=True)
    data['Date'] = data['Date'].astype('str')
    data['Date'] = data['Date'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y'))
    data['Year'] = data['Date'].dt.year

    data.rename(columns={"Near term - Target Status": "target_status", "Location": "Country"}, inplace=True)
    return data

def display_bar_chart(df: pd.DataFrame) -> None:
    """
    Display a bar chart showing the number of companies with approved and committed target status per country.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing the company data.

    Returns:
    None.
    """

    st.title("Number of Companies with Approved and Committed Target Status per Country")
    option = st.radio("Show data grouped by", ("country", "year"))

    if option == "country":
        grouped = df.groupby(["Country", "target_status"]).count().reset_index()
        pivot = grouped.pivot(index="Country", columns="target_status", values="Company Name").fillna(0)
        pivot.sort_values("Targets Set", ascending=False, inplace=True)

        countries = pivot.index.tolist()
        n = len(countries)
        num_per_plot = st.slider("Number of Countries per Plot", min_value=1, max_value=n, value=15, step=1)
        num_plots = n // num_per_plot + 1
        for i in range(num_plots):
            fig, ax = plt.subplots()
            pivot.loc[countries[i*num_per_plot:(i+1)*num_per_plot]].plot(kind="bar", stacked=False, ax=ax, color=["blue", "red"])
            ax.legend(["SBTI approved", "Committed"])
            st.pyplot(fig)
        
    else:
        countries = sorted(df["Country"].unique().tolist())
        country = st.selectbox("Select a country", countries)
        grouped = df[df["Country"] == country].groupby(["Year", "target_status"]).count().reset_index()
        pivot = grouped.pivot(index="Year", columns="target_status", values="Company Name").fillna(0)
        pivot.sort_values("Year", ascending=True, inplace=True)

        pivot = pivot.rename(columns={"Targets Set": "SBTi approved", "Committed": "Committed"})
        fig, ax = plt.subplots()
        pivot.plot(kind="bar", stacked=False, ax=ax, color=["blue", "red"])
        ax.legend(["SBTI approved", "Committed"])
        st.pyplot(fig)
        

if __name__=="__main__":
    data = get_file(CTA_URL)
    display_bar_chart(data)
 
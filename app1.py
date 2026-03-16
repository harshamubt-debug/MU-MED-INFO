import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import feedparser
from Bio import Entrez

# -----------------------------
# PAGE SETTINGS
# -----------------------------

st.set_page_config(page_title="MU MED-INFO", layout="wide")

st.title("MU MED-INFO")
st.subheader("Real-time Global Disease Surveillance Dashboard")

st.markdown(
"Integrating epidemiological data and outbreak alerts from global public health surveillance systems."
)

# -----------------------------
# SEARCH
# -----------------------------

disease = st.text_input("Search Disease")

# -----------------------------
# GLOBAL COVID DATA (Disease.sh)
# -----------------------------

try:
    url = "https://disease.sh/v3/covid-19/all"
    data = requests.get(url).json()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Cases", data["cases"])
    col2.metric("Total Deaths", data["deaths"])
    col3.metric("Recovered", data["recovered"])
    col4.metric("Active", data["active"])

except:
    st.error("Unable to fetch global data")

# -----------------------------
# COUNTRY DATA
# -----------------------------

st.header("Global Disease Map")

try:

    url = "https://disease.sh/v3/covid-19/countries"
    data = requests.get(url).json()

    df = pd.json_normalize(data)

    df = df[[
        "country",
        "cases",
        "deaths",
        "recovered",
        "countryInfo.lat",
        "countryInfo.long"
    ]]

    df.columns = ["Country","Cases","Deaths","Recovered","Lat","Long"]

    fig = px.scatter_geo(
        df,
        lat="Lat",
        lon="Long",
        size="Cases",
        hover_name="Country",
        color="Cases",
        projection="natural earth"
    )

    st.plotly_chart(fig, use_container_width=True)

except:
    st.warning("Map data unavailable")

# -----------------------------
# TOP COUNTRIES GRAPH
# -----------------------------

st.header("Top 10 Countries by Cases")

try:

    top10 = df.sort_values("Cases", ascending=False).head(10)

    fig2 = px.bar(
        top10,
        x="Country",
        y="Cases",
        color="Cases"
    )

    st.plotly_chart(fig2, use_container_width=True)

except:
    st.warning("Graph unavailable")

# -----------------------------
# GENOMIC DATA (NCBI)
# -----------------------------

st.header("Genomic Information")

Entrez.email = "your_email@gmail.com"

if disease:

    try:

        search = Entrez.esearch(db="nucleotide", term=disease, retmax=1)
        record = Entrez.read(search)

        if record["IdList"]:

            genome_id = record["IdList"][0]

            fetch = Entrez.efetch(
                db="nucleotide",
                id=genome_id,
                rettype="gb",
                retmode="text"
            )

            genome = fetch.read()

            st.text(genome[:800])

        else:
            st.write("No genome found")

    except:
        st.write("Genome data unavailable")

# -----------------------------
# OUTBREAK ALERTS (ProMED)
# -----------------------------

st.header("Latest Outbreak Alerts")

try:

    feed = feedparser.parse("https://promedmail.org/rss/")

    for entry in feed.entries[:5]:

        st.write("🔴", entry.title)
        st.write(entry.link)
        st.write("---")

except:
    st.write("Alert feed unavailable")

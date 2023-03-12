import pandas as pd
import requests
import streamlit as st

FASTAPI_ENDPOINT = "http://sgde_api:8000"
GENERATORS_ENDPOINT = f"{FASTAPI_ENDPOINT}/generators/"
response = requests.get(GENERATORS_ENDPOINT)

st.set_page_config(page_title="SGDE - Explore", page_icon=":earth_africa:")
st.header(":earth_africa: Explore")

generators = response.json()


def download_generator_fn(name: str):
    try:
        url = f"{GENERATORS_ENDPOINT}{name}/download"
        requests.get(url, headers={"Authorization": f"Bearer {st.session_state['access_token']}"})
    except KeyError:
        st.error("You must login first.")


for g in generators:
    g["download"] = st.button("Download", on_click=download_generator_fn, args=(g["name"],))

df = pd.DataFrame(generators)
st.table(df)

import pandas as pd
import requests
import streamlit as st

FASTAPI_ENDPOINT = "http://127.0.0.1:8000/generators"

response = requests.get(FASTAPI_ENDPOINT)

st.session_state.page = 1

st.set_page_config(page_title="SGDE - Explore", page_icon=":earth_africa:")
st.header(":earth_africa: Explore")

generators = pd.DataFrame(response.json())
st.table(generators)

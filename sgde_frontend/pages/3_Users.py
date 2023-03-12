import pandas as pd
import requests
import streamlit as st

FASTAPI_ENDPOINT = "http://sgde_api:8000/users/"
response = requests.get(FASTAPI_ENDPOINT)

st.set_page_config(page_title="SGDE - Users", page_icon=":nerd_face:")
st.header(":nerd_face: Users")

users = pd.DataFrame(response.json())
st.table(users)

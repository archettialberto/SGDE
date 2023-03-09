from datetime import datetime

import streamlit as st

items = [{"name": f"items{i}", "size": {i}, "date": datetime.utcnow()} for i in range(100)]

FASTAPI_ENDPOINT = "http://localhost:8000/generators"
PAGE_SIZE = 10

st.session_state.page = 1

st.set_page_config(page_title="SGDE - Explore", page_icon=":earth_africa:")
st.header(":earth_africa: Explore")

st.table(items)

import pandas as pd
import requests
import streamlit as st

FASTAPI_ENDPOINT = "http://sgde_api:8000"
GENERATORS_ENDPOINT = f"{FASTAPI_ENDPOINT}/generators/"
response = requests.get(GENERATORS_ENDPOINT)

st.set_page_config(
    page_title="SGDE - Explore", page_icon=":earth_africa:", layout="wide"
)
st.header(":earth_africa: Explore")

generators = response.json()
df = pd.DataFrame(generators)

st.sidebar.subheader("Filter")
name_filter = st.sidebar.text_input("Name contains")

filtered_df = df[df["name"].str.contains(name_filter)]

st.sidebar.subheader("Sort")
sort_by = st.sidebar.selectbox("Sort by", ["name"])

sorted_df = filtered_df.sort_values(by=sort_by)

if len(sorted_df) == 0:
    st.write("No generators found.")
else:
    columns = list(df.columns)
    excluded_columns = ["conditioned", "batch_size", "description"]
    for c in excluded_columns:
        columns.remove(c)
    cols = st.columns(len(columns) + 1)
    for col, col_name in zip(cols[:-1], columns):
        if col_name not in excluded_columns:
            with col:
                st.write(col_name)
    with cols[-1]:
        st.write("Download")
    sorted_df = sorted_df.reset_index(drop=True)
    for i in range(len(sorted_df)):
        for col, col_name in zip(cols[:-1], columns):
            if col_name not in excluded_columns:
                with col:
                    st.write(sorted_df.loc[i, col_name])
        with cols[-1]:
            st.download_button(label=":arrow_down:", data=sorted_df.loc[i, "name"])

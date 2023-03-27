import pandas as pd
import requests
import streamlit as st

# Retrieve generators
FASTAPI_ENDPOINT = "http://sgde_api:8000"
GENERATORS_ENDPOINT = f"{FASTAPI_ENDPOINT}/generators/"
response = requests.get(GENERATORS_ENDPOINT)
generators = response.json()
df = pd.DataFrame(generators)

# Configure webpage
st.set_page_config(
    page_title="SGDE - Explore", page_icon=":earth_africa:", layout="wide"
)
st.header(":earth_africa: Explore")

# Filter generators
st.sidebar.subheader("Filter")
name_filter = st.sidebar.text_input("Name contains")
if len(df) > 0:
    filtered_df = df[df["name"].str.contains(name_filter)]
else:
    filtered_df = df

# Sort generators
st.sidebar.subheader("Sort")
sort_by = st.sidebar.selectbox("Sort by", ["name"])
if len(filtered_df) > 0:
    sorted_df = filtered_df.sort_values(by=sort_by)
else:
    sorted_df = filtered_df


st.session_state["onnx_cache"] = b""


def on_clock_download(generator_name: str):
    r = requests.get(f"{GENERATORS_ENDPOINT}/{generator_name}/download")
    if r.status_code != 200:
        st.error(f"Generator {generator_name} cannot be retrieved")
    else:
        st.session_state["onnx_cache"] = r.content


# Display generators table
display_columns = {
    "name": "Name",
    "owner": "Owner",
    "data_format": "Data Format",
    "task": "Task",
    "model_size": "Size",
}

# Display table header
st_columns = st.columns(len(display_columns) + 1)
for st_col, col_name in zip(st_columns[:-1], display_columns.keys()):
    with st_col:
        st.write(display_columns[col_name])
with st_columns[-1]:
    st.write("Download")

# Display generators
if len(sorted_df) == 0:
    st.write("No generators found.")
else:
    sorted_df = sorted_df.reset_index(drop=True)
    for i in range(len(sorted_df)):
        for st_col, col_name in zip(st_columns[:-1], display_columns.keys()):
            with st_col:
                st.write(sorted_df.loc[i, col_name])
        with st_columns[-1]:
            st.download_button(
                label=":arrow_down:",
                on_click=on_clock_download,
                args=(sorted_df.loc[i, 'name']),
                data=st.session_state["onnx_cache"],
            )

import streamlit as st
import requests

FASTAPI_ENDPOINT = "http://sgde_api:8000/exchange/upload"

st.set_page_config(page_title="SGDE - Upload", page_icon=":arrow_up_small:")

st.header(":arrow_up_small: Upload")
st.write("Please fill the generator upload form:")
name = st.text_input("Generator name")
conditioned = st.checkbox("Conditioned")
data_format = st.selectbox("Data format", ["image"])
task = st.selectbox("Task", ["classification", "regression"])

if task == "classification":
    num_classes = st.number_input("Number of classes", 1, 1000)
else:
    num_classes = None

model_size = st.selectbox("Model size", ["small", "medium", "large"])

epochs = st.number_input("Epochs", 1, 1000)
batch_size = st.number_input("Batch size", 1, 1000)
description = st.text_area("Description")

file_uploader = st.file_uploader("Choose a file")

upload_button = st.button("Upload")

if upload_button:
    upload_data = {
        "name": name,
        "conditioned": conditioned,
        "data_format": data_format,
        "task": task,
        "num_classes": num_classes,
        "model_size": model_size,
        "epochs": epochs,
        "batch_size": batch_size,
        "description": description,
    }
    try:
        response = requests.post(
            FASTAPI_ENDPOINT,
            headers={"Authorization": f"Bearer {st.session_state['access_token']}"},
            data=upload_data,
            files={
                "onnx_file": file_uploader.getvalue()
                if file_uploader is not None
                else None
            },
        )
        if response.status_code == 201:
            st.success("Upload successful!")
        else:
            st.error(f"Upload failed. {response.text}")
    except KeyError:
        st.error("Please login first.")
    except requests.exceptions.ConnectionError:
        st.error("The server is unreachable.")

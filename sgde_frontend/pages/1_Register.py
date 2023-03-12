import streamlit as st
import requests

FASTAPI_ENDPOINT = "http://sgde_api:8000/auth/register"

st.set_page_config(page_title="SGDE - Register", page_icon=":pencil:")

st.header(":pencil: Register")
st.write("Please fill the registration form:")
username = st.text_input("Username")
email = st.text_input("Email")
password = st.text_input("Password", type="password")
register_button = st.button("Register")

if register_button:
    register_data = {"username": username, "email": email, "password": password}
    try:
        response = requests.post(FASTAPI_ENDPOINT, json=register_data)
        if response.status_code == 201:
            st.success("Registration successful!")
        else:
            st.error(f"Registration failed. {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("The server is unreachable.")

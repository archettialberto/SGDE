import streamlit as st
import requests

FASTAPI_ENDPOINT = "http://localhost:8000/auth/login"

st.set_page_config(page_title="SGDE - Login", page_icon=":key:")

st.header(":key: Login")
st.write("Please enter your login credentials:")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
login_button = st.button("Login")

if login_button:
    login_data = {"username": username, "password": password}
    try:
        response = requests.post(FASTAPI_ENDPOINT, json=login_data)
        if response.status_code == 200:
            st.success("Login successful!")
        else:
            st.error("Login failed. Please check your credentials.")
    except requests.exceptions.ConnectionError:
        st.error("The server is unreachable.")

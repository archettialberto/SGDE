import streamlit as st
import requests

FASTAPI_ENDPOINT = "http://sgde_api:8000"
LOGIN_ENDPOINT = f"{FASTAPI_ENDPOINT}/auth/token"
WHOAMI_ENDPOINT = f"{FASTAPI_ENDPOINT}/auth/whoami"

st.set_page_config(page_title="SGDE - Login", page_icon=":key:")

st.header(":key: Login")
st.write("Please enter your login credentials:")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
login_button = st.button("Login")
whoami_button = st.button("Whoami")

if login_button:
    login_data = {"username": username, "password": password}
    try:
        response = requests.post(LOGIN_ENDPOINT, data=login_data)
        if response.status_code == 200:
            st.session_state["access_token"] = response.json()["access_token"]
            st.success("Login successful!")
        else:
            st.error(f"Login failed. {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("The server is unreachable.")

if whoami_button:
    try:
        response = requests.get(
            WHOAMI_ENDPOINT,
            headers={"Authorization": f"Bearer {st.session_state['access_token']}"}
        )
        if response.status_code == 200:
            st.success(f"You are logged in as {response.json()['username']} ({response.json()['email']}).")
        else:
            st.error(f"Login failed. {response.text}")
    except KeyError:
        st.error("Please login first.")
    except requests.exceptions.ConnectionError:
        st.error("The server is unreachable.")

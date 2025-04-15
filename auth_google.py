import streamlit as st
from streamlit_google_auth import Authenticate
import os # To construct path safely

# --- Configuration ---
# Determine the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Define the path to the credentials file relative to the script's directory
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'google_credentials.json')

# Use Streamlit secrets for sensitive info
COOKIE_NAME = st.secrets.get("cookie_config", {}).get("name", "my_cookie_name")
COOKIE_KEY = st.secrets.get("cookie_config", {}).get("key", "default_secret_key") # Use a default only if secret is missing, less secure
COOKIE_EXPIRY_DAYS = st.secrets.get("cookie_config", {}).get("expiry_days", 30)

# IMPORTANT: Replace with your actual Codespaces forwarded URL or deployed app URL
# Use st.secrets if you plan to deploy, otherwise hardcode for testing ONLY
REDIRECT_URI = st.secrets.get("auth_config", {}).get("redirect_uri", "http://localhost:8501")
# Example for secrets.toml:
# [auth_config]
# redirect_uri = "YOUR_CODESPACES_URL_HERE"

# Function to initialize the Authenticate object
def initialize_authenticator():
    """Initializes and returns the Authenticate object."""
    # Check if credentials file exists
    if not os.path.exists(CREDENTIALS_PATH):
         st.error(f"Credentials file not found at: {CREDENTIALS_PATH}")
         st.stop() # Stop execution if secrets file is missing

    # Check if cookie key is the default (less secure)
    if COOKIE_KEY == "default_secret_key":
        st.warning("Using default cookie key. Please set a secret key in secrets.toml for security.")

    try:
        authenticator = Authenticate(
            secret_credentials_path=CREDENTIALS_PATH,
            cookie_name=COOKIE_NAME,
            cookie_key=COOKIE_KEY,
            redirect_uri=REDIRECT_URI,
            cookie_expiry_days=COOKIE_EXPIRY_DAYS
        )
        return authenticator
    except Exception as e:
        st.error(f"Error initializing authenticator: {e}")
        st.stop() # Stop execution on initialization error
        return None # Keep linters happy


# Function to handle the login flow
def handle_auth_flow(authenticator):
    """Runs the authentication check and displays the login button."""
    if authenticator:
        authenticator.check_authentification() # Important: Catches the redirect back from Google
        authenticator.login() # Renders the login button if not authenticated


# Function to handle logout
def handle_logout(authenticator):
    """Renders the logout button and handles the logout action."""
    if authenticator and st.session_state.get("connected"): # Only show if connected
         if st.sidebar.button("Log out"): # Place logout in sidebar
            authenticator.logout()
            st.rerun() # Rerun the app to reflect the logged-out state immediately
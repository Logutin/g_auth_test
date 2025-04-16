import streamlit as st
from streamlit_google_auth import Authenticate
import os
import json # <-- Add import

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_CREDENTIALS_PATH = os.path.join(BASE_DIR, 'google_credentials.json')
# Define path for temporary file on Streamlit Cloud (usually writable)
CLOUD_CREDENTIALS_PATH = "/tmp/google_credentials.json"

COOKIE_NAME = st.secrets.get("cookie_config", {}).get("name", "my_cookie_name")
COOKIE_KEY = st.secrets.get("cookie_config", {}).get("key", "default_secret_key")
COOKIE_EXPIRY_DAYS = st.secrets.get("cookie_config", {}).get("expiry_days", 30)
REDIRECT_URI = st.secrets.get("auth_config", {}).get("redirect_uri", "http://localhost:8501") # Will be set in Cloud secrets

# Function to write secrets to a temporary JSON file for Streamlit Cloud
def write_cloud_credentials():
    """Reads Google credentials from st.secrets and writes them to a temporary file."""
    creds = st.secrets.get("google_credentials")
    if not creds:
        st.error("Google credentials not found in Streamlit Secrets ([google_credentials] section).")
        st.stop()
        return None # Keep linters happy

    # Construct the dictionary structure expected by the credentials file
    credentials_content = {"web": dict(creds)} # Convert TomlTable to dict

    try:
        with open(CLOUD_CREDENTIALS_PATH, "w") as f:
            json.dump(credentials_content, f)
        print(f"DEBUG: Successfully wrote cloud credentials to {CLOUD_CREDENTIALS_PATH}")
        return CLOUD_CREDENTIALS_PATH
    except Exception as e:
        st.error(f"Failed to write temporary credentials file: {e}")
        st.stop()
        return None

# Updated Function to initialize the Authenticate object
def initialize_authenticator():
    """Initializes and returns the Authenticate object, handling local vs cloud."""
    credentials_path_to_use = None

    # Check if running on Streamlit Cloud by checking for a specific secret key existence
    # Alternatively, use environment variables if available and reliable
    if "google_credentials" in st.secrets:
        print("DEBUG: Detected Streamlit Cloud environment (found google_credentials in secrets).")
        credentials_path_to_use = write_cloud_credentials()
    else:
        print("DEBUG: Detected local environment (google_credentials not found in secrets).")
        if os.path.exists(LOCAL_CREDENTIALS_PATH):
            credentials_path_to_use = LOCAL_CREDENTIALS_PATH
        else:
            st.error(f"Local credentials file not found at: {LOCAL_CREDENTIALS_PATH}")
            st.stop() # Stop execution if local secrets file is missing

    if not credentials_path_to_use:
         st.error("Could not determine or create credentials path.")
         st.stop() # Stop if we don't have a valid path

    # Check if cookie key is the default (less secure)
    if COOKIE_KEY == "default_secret_key":
        st.warning("Using default cookie key. Please set a secret key in secrets.toml for security.")

    # Check if Redirect URI is placeholder (common deploy issue)
    if not REDIRECT_URI or REDIRECT_URI == "http://localhost:8501":
         st.warning(f"Redirect URI is not set or is default localhost ({REDIRECT_URI}). Ensure it's correctly set in Streamlit Secrets ([auth_config] -> redirect_uri) for deployment.")


    try:
        print(f"DEBUG: Initializing Authenticate with path: {credentials_path_to_use}")
        authenticator = Authenticate(
            secret_credentials_path=credentials_path_to_use, # Use the determined path
            cookie_name=COOKIE_NAME,
            cookie_key=COOKIE_KEY,
            redirect_uri=REDIRECT_URI,
            cookie_expiry_days=COOKIE_EXPIRY_DAYS
        )
        print("DEBUG: Authenticate object created successfully.")
        return authenticator
    except Exception as e:
        st.error(f"Error initializing authenticator: {e}")
        # Optionally print args again if error persists
        # print(f"DEBUG Args at error: path={credentials_path_to_use}, cookie={COOKIE_NAME}, key={COOKIE_KEY}, uri={REDIRECT_URI}, expiry={COOKIE_EXPIRY_DAYS}")
        st.stop()
        return None

# Function to handle the login flow
def handle_auth_flow(authenticator):
    """
    Runs the authentication check and displays the login button
    (modified to use target='_top').
    """
    if authenticator:
        # This part remains the same - it handles the redirect *back* from Google
        # authenticator.check_authentification()

        # Check connection status *after* check_authentification might have updated it
        if not st.session_state.get("connected"):
            try:
                auth_url = authenticator.get_authorization_url()

                # --- Use st.link_button ---
                # This component is specifically designed for navigation links
                # that look like buttons. It might handle the iframe context better.
                # It doesn't need target="_top" or onclick JS.
                st.link_button("Sign in with Google", auth_url, type="primary", help="Click to sign in via your Google account")

            except Exception as e:
                st.error(f"Error generating login link: {e}")
        # Original authenticator.login() is now replaced by the markdown above
        # authenticator.login()

# Function to handle logout
def handle_logout(authenticator):
    """Renders the logout button and handles the logout action."""
    if authenticator and st.session_state.get("connected"): # Only show if connected
         if st.sidebar.button("Log out"): # Place logout in sidebar
            authenticator.logout()
            st.rerun() # Rerun the app to reflect the logged-out state immediately
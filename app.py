import streamlit as st
from auth import load_config, initialize_authenticator, handle_login # Import functions from auth.py

# --- Page Configuration ---
# Set page title and potentially layout. Run this first.
# We can set the page title here, but it might be visible before login.
# Consider setting a generic title initially if secrecy is paramount.
st.set_page_config(page_title="Protected App", layout="centered")

# --- Authentication ---
config = load_config()

if config: # Proceed only if config loaded successfully
    authenticator = initialize_authenticator(config)

    if authenticator:
        # Render the login/logout interface handle_login also implicitly updates session state
        # It will show the login button or handle the OAuth callback.
        # We don't necessarily need the return values here if checking session state directly.
        handle_login(authenticator)

        # Check authentication status FROM SESSION STATE
        auth_status = st.session_state.get('authentication_status')
        user_name = st.session_state.get('name')
        # user_username = st.session_state.get('username') # Internal key, might not need

        if auth_status is True:
            # --- User is Logged In ---
            st.sidebar.write(f"Welcome, *{user_name}*!")
            authenticator.logout("Logout", "sidebar") # Place logout button in sidebar

            # --- Main App Content ---
            st.title("🎈 My Super Secret App")
            st.write("You are successfully logged in!")

            if st.button("Show Balloons!"):
                st.balloons()
                st.success("Woohoo! Balloons!")

            # Add other app logic here...
            st.info("This content is only visible after successful Google authentication.")


        elif auth_status is False:
            # --- Login Failed ---
            st.error("Login failed. Please check if your email is authorized or try again.")
            # The handle_login function likely already showed an error,
            # but we can add another general message here.

        elif auth_status is None:
            # --- User Not Logged In ---
            st.info("Please log in using the button above to access the application.")
            # The login button is rendered by handle_login

    else:
        # Handle case where authenticator initialization failed
        st.error("Authenticator could not be initialized. Check logs or configuration.")
else:
    # Handle case where config loading failed
     st.error("Application configuration could not be loaded. Cannot proceed.")

# --- Footer or other elements visible to all ---
# st.markdown("---")
# st.caption("A test app by Me")
import streamlit as st
from auth_google import initialize_authenticator, handle_auth_flow, handle_logout # Import from our new module

# --- Page Configuration ---
st.set_page_config(page_title="Google Auth App", layout="centered")

# --- Authorization Configuration ---
# Define the list of emails allowed to access this app
# For simplicity, hardcoded here. Consider moving to st.secrets for better management.
# Example using secrets.toml:
# ALLOWED_EMAILS = st.secrets.get("authorization", {}).get("allowed_emails", [])
ALLOWED_EMAILS = [
    "your_google_email@example.com", # <-- *** REPLACE with YOUR Google email ***
    "colleague1@example.com",      # <-- Add your colleagues' emails
    "colleague2@yourcompany.com",
    # Add all emails that should have access
]

# --- Authentication ---
authenticator = initialize_authenticator()

if authenticator:
    # Display login button and handle authentication callbacks
    handle_auth_flow(authenticator)

    # --- Authorization & App Logic ---
    # Check if user is connected (logged in via Google)
    if st.session_state.get("connected"):
        user_email = st.session_state.get("user_info", {}).get("email")
        user_name = st.session_state.get("user_info", {}).get("name", "User")
        user_picture = st.session_state.get("user_info", {}).get("picture")

        # **Authorization Check**
        if user_email in ALLOWED_EMAILS:
            # --- User is Authenticated AND Authorized ---

            # Display user info and logout button in sidebar
            if user_picture:
                st.sidebar.image(user_picture, width=75)
            st.sidebar.write(f"Welcome, *{user_name}*!")
            st.sidebar.write(f"*{user_email}*")
            handle_logout(authenticator) # Renders logout button in sidebar

            # --- Main App Content ---
            st.title("🎈 My Authorized App")
            st.success("You are successfully logged in and authorized!")

            if st.button("Show Balloons!"):
                st.balloons()
                st.info("Balloons launched!")

            st.info("This content is only visible to authorized users.")
            # Add the rest of your app logic here

        else:
            # --- User is Authenticated BUT NOT Authorized ---
            st.error(f"Access Denied: Your email ({user_email}) is not authorized to use this application.")
            st.warning("Please contact the administrator if you believe this is an error.")
            # Log the user out immediately as they shouldn't be here
            authenticator.logout()
            # Consider adding st.rerun() if logout doesn't clear state fast enough

    elif "connected" in st.session_state and st.session_state["connected"] is False:
         # Optional: Handle case where check_authentification might have failed explicitly
         st.warning("Login attempt failed or session expired.")
         # Login button is already rendered by handle_auth_flow

    else:
         # --- User Not Logged In ---
         st.info("Please log in using the Google button above to access the application.")
         # Login button is rendered by handle_auth_flow

else:
    # Error during authenticator initialization (message handled in auth_google.py)
    st.warning("Authentication system failed to initialize.")

# --- Footer ---
# st.markdown("---")
# st.caption("Google Auth Test App")
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Function to load configuration from YAML file
def load_config(filepath="config.yaml"):
    """Loads the authenticator configuration from a YAML file."""
    try:
        with open(filepath, 'r') as file:
            config = yaml.load(file, Loader=SafeLoader)
        return config
    except FileNotFoundError:
        st.error(f"Configuration file not found at {filepath}")
        return None
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        return None

# Function to initialize the authenticator
def initialize_authenticator(config):
    """Initializes the Streamlit Authenticator object."""
    if not config:
        return None

    # Read Google credentials from Streamlit secrets
    google_client_id = st.secrets.get("GOOGLE_CLIENT_ID")
    google_client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET")

    if not google_client_id or not google_client_secret:
        st.error("Google Client ID or Secret not found in secrets.toml")
        return None

    # Check if providers config exists and update Google provider credentials
    if 'providers' in config:
        for provider in config['providers']:
            if provider.get('name') == 'Google':
                # Inject secrets into the specific provider config
                provider['client_id'] = google_client_id
                provider['client_secret'] = google_client_secret
                # Remove if they were accidentally left in config.yaml
                # (though we explicitly didn't put them there)
                provider.pop('client_id', None) # Ensure clean state
                provider.pop('client_secret', None) # Ensure clean state
                # Now re-add from secrets
                provider['client_id'] = google_client_id
                provider['client_secret'] = google_client_secret
    else:
        st.warning("OAuth providers section missing in config.yaml")
        # If you want to proceed without OAuth if section is missing, handle accordingly
        # For now, we assume it's required.
        return None


    try:
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
            config['preauthorized'],
            config.get('providers') # Pass the updated providers list
        )
        return authenticator
    except KeyError as e:
        st.error(f"Missing key in config.yaml: {e}. Please check your configuration.")
        return None
    except Exception as e:
        st.error(f"Error initializing authenticator: {e}")
        return None


# Function to handle the login process and render the login form
def handle_login(authenticator):
    """
    Handles the login flow. Renders the login form and returns
    authentication status, name, and username upon successful login.

    Returns:
        tuple: (auth_status, name, username)
               auth_status (bool or None): True if authenticated, False if failed, None if login pending.
               name (str or None): User's name if authenticated.
               username (str or None): User's internal username key if authenticated.
    """
    if not authenticator:
        return None, None, None

    try:
        # Render the login widget
        # Using 'main' location renders it directly on the page
        # Using 'sidebar' renders it in the sidebar
        # Using a form is generally recommended for login flows
        with st.container(): # Use a container to group login elements
             # Check if OAuth providers are configured
            if authenticator.providers:
                # Display OAuth login buttons only
                auth_status, name, username = authenticator.login(fields={}, location='main')

            else:
                 # Fallback or error if no providers configured but expected
                st.warning("No OAuth providers configured.")
                # If you had password auth, the standard login would go here
                # name, auth_status, username = authenticator.login("Login", "main")
                return None, None, None # Indicate login cannot proceed

        return auth_status, name, username

    except Exception as e:
        st.error(f"An error occurred during login: {e}")
        return False, None, None # Indicate login failed
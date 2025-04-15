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
        # --- BEGIN DEBUG PRINTS ---
        print("-" * 30)
        print("DEBUG: Preparing to initialize Authenticate")

        creds = config.get('credentials')
        cookie_name = config.get('cookie', {}).get('name')
        cookie_key = config.get('cookie', {}).get('key')
        cookie_expiry = config.get('cookie', {}).get('expiry_days')
        providers_config = config.get('providers')

        print(f"DEBUG: credentials type: {type(creds)}, value: {creds}")
        print(f"DEBUG: cookie_name type: {type(cookie_name)}, value: '{cookie_name}'") # Put quotes around value for clarity
        print(f"DEBUG: cookie_key type: {type(cookie_key)}, value: '{cookie_key}'")   # Put quotes around value for clarity
        print(f"DEBUG: cookie_expiry type: {type(cookie_expiry)}, value: {cookie_expiry}")
        print(f"DEBUG: providers_config type: {type(providers_config)}, value: {providers_config}")
        print("-" * 30)
        # --- END DEBUG PRINTS ---
        # --- TEST INITIALIZATION (omit providers) ---
        print("DEBUG: Attempting initialization with core 4 arguments...")
        authenticator = stauth.Authenticate(
            creds,
            cookie_name,
            cookie_key,
            cookie_expiry
            # providers_config # <-- Temporarily OMITTED for this test
        )
        print("DEBUG: Authenticate initialized successfully (without providers)")
        # We know this authenticator object won't work for OAuth yet,
        # but we just want to see if it initializes without TypeError.
        # For now, let's return None to prevent further issues down the line in this test scenario
        # If it succeeds, we know the core init is okay.
        # return authenticator # Don't return the incomplete object yet
        st.warning("DEBUG: Initialization successful WITHOUT providers. Next step is to add them correctly.")
        return None # Force app to show an error, indicating test progress

    except KeyError as e:
        st.error(f"Missing key in config.yaml: {e}. Please check your configuration.")
        print(f"DEBUG: KeyError during initialization: {e}") # Debug print for errors
        return None
    except TypeError as e:
        st.error(f"Type error during initialization: {e}. Check config values (especially cookie key/name).")
        print(f"DEBUG: TypeError during initialization: {e}") # Debug print for errors
        # Optionally print the arguments again here if helpful
        print(f"DEBUG: Args at TypeError: creds={creds}, name={cookie_name}, key={cookie_key}, expiry={cookie_expiry}, providers={providers_config}")
        return None
    except Exception as e:
        st.error(f"Error initializing authenticator: {e}")
        print(f"DEBUG: Generic Exception during initialization: {e}") # Debug print for errors
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
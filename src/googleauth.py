import datetime
import requests

from src.config import Config
from datetime import datetime, timedelta
from google.oauth2 import id_token
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = Config.GOOGLE_CLIENT_SECRET
GOOGLE_CLIENT_CONFIG = Config.GOOGLE_CLIENT_JSON
SCOPES = Config.GOOGLE_AUTH_SCOPE


def get_user_info(credentials):
    token_request = Request(session=requests.session())
    try:
        info = id_token.verify_oauth2_token(id_token=credentials.id_token, request=token_request, audience=GOOGLE_CLIENT_ID)
        return info
    except Exception as e:
        raise Exception(f"Error occured: {e}")

def refresh_token(credentials):
    params = {
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "refresh_token": credentials.refresh_token,
        "grant_type": "refresh_token"
    }

    try:
        response = requests.post("https://oauth2.googleapis.com/token", data=params)
        response.raise_for_status()
        # Calculate the new expiry date based on the current time and the expires_in value in the response
        new_expiry = datetime.now() + timedelta(seconds=response.json()['expires_in'])

        # Create the new Credentials object with the updated access token and expiry date
        new_credentials = Credentials(
            token=response.json()['access_token'],
            refresh_token=credentials.refresh_token,
            token_uri=credentials.token_uri,
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=SCOPES,
            expiry=new_expiry
        )
        return new_credentials
    except requests.exceptions.HTTPError as error:
        # Handle HTTP errors
        raise Exception(f"HTTP error occurred: {error}")
    
    except Exception as error:
        raise Exception(f"Error occured: {error}")
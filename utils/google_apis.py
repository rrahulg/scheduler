import os
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from utils.logger import CustomException, logging


def get_google_calendar_service(client_secrets_file, token_file, SCOPES):
    """Builds and returns an authenticated Google Calendar API service.

    Args:
        client_secrets_file (str): Path to the client secret JSON file.
        token_file (str): Path to the token JSON file.
        SCOPES (List[str]): List of scopes for Google Calendar API access.

    Returns:
        _type_: Authorized Google Calendar service instance.
    """
    CLIENT_SECRETS_FILE = client_secrets_file
    TOKEN_FILE = token_file
    creds = None

    try:
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            logging.info("Using existing authorized token file.")

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                logging.info("Credentials refreshed successfully.")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRETS_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)
                logging.info("New credentials generated via OAuth flow.")

            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
                logging.info(f"Credentials saved to token file: {TOKEN_FILE}")

        service = build("calendar", "v3", credentials=creds)
        logging.info("Google Calendar service initialized successfully.")
        return service

    except Exception as e:
        logging.error("Unable to build Google Calendar service.")
        raise CustomException(e, sys)

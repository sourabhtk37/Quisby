import pickle
import os.path

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import google.auth

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def authenticate_creds():
    """
    Authenticate credentials
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds


# def authenticate_creds():
#     creds = None
#     # The file token.pickle stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if os.path.exists("token_auto.pickle"):
#         with open("token_auto.pickle", "rb") as token:
#             creds = pickle.load(token)
#     if not creds or not creds.valid:
#         try:
#             creds, project = google.auth.default(scopes=SCOPES)

#             with open("token_auto.pickle", "wb") as token:
#                 pickle.dump(creds, token)
#         except Exception as err:
#             creds = authenticate_creds_via_credentials

#     return creds

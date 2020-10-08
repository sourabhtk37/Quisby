from googleapiclient.discovery import build

from credentials.creds import authenticate_creds


creds = authenticate_creds()
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

import pickle
import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def read_sheet(sheet, spreadsheet_Id, range='A:F'):
    """
    """
    result = sheet.values().get(spreadsheetId=spreadsheet_Id,
                                range=range).execute()
    values = result.get('values', [])

    return values


def append_to_sheet(sheet, spreadsheet_Id, results, range='A:F'):
    """
    """

    body = {
        'values': results
    }

    response = sheet.values().append(spreadsheetId=spreadsheet_Id,
                                     range=range,
                                     valueInputOption='USER_ENTERED',
                                     body=body).execute()
    return response


def authenticate_creds():
    """
    Authenticate credentials
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def apply_named_range(sheet, spreadsheetId, name, range='A:F'):

    sheetId = get_sheet(sheet, spreadsheetId, range)[
        'sheets'][0]['properties']['sheetId']

    sheet_range = range.split('!')[1].split(':')

    body = {
        "requests": [{
            "addNamedRange": {
                "namedRange": {
                    "namedRangeId": range,
                    "name": name+"_NR",
                    "range": {
                        "sheetId": sheetId,
                        "startRowIndex": int(sheet_range[0][1:]) - 1,
                        "endRowIndex": sheet_range[1][1:],
                        "startColumnIndex": ord(sheet_range[0][:1]) % 65,
                        "endColumnIndex": ord(sheet_range[1][:1]) % 65 + 1
                    }
                }
            },
        }
        ]
    }

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheetId, body=body).execute()

    print(response)


def get_sheet(sheet, spreadsheetId, range='A:F'):

    return sheet.get(spreadsheetId=spreadsheetId,
                     ranges=range).execute()


def clear_sheet_data(sheet, spreadsheetId, range='A2:Z1000'):
    # Clear values
    sheet.values().clear(spreadsheetId=spreadsheetId,
                         range=range, body={}).execute()


def clear_sheet_charts(sheet, spreadsheetId, range='A2:Z1000'):
    # Clear charts
    sheet_properties = get_sheet(sheet, spreadsheetId, range)

    if 'charts' in sheet_properties['sheets'][0]:
        for chart in sheet_properties['sheets'][0]['charts']:

            requests = {
                "deleteEmbeddedObject": {
                    "objectId": chart['chartId']
                }
            }

            body = {
                "requests": requests
            }

            sheet.batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()


def get_named_range(sheet, spreadsheetId, range='A:F'):
    spreadsheet = get_sheet(sheet, spreadsheetId, range)

    # print(spreadsheet['namedRanges'])

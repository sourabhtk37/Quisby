import pickle
import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

from get_aws_pricing import get_ondemand_hourly_price
from stream_parse import extract_stream_data


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# ToDo: Check first if spreadsheet exists and then check if corresponding sheet for test is created, else create


def create_sheet(sheet, test_name, spreadsheet_Id):
    if test_name == 'linpack':
        spreadsheet = {
            'properties': {
                'title': test_name
            },
            'sheets': {
                'properties': {
                    'sheetId': 0,
                    'title': test_name,
                    'gridProperties': {
                        'frozenRowCount': 1,
                    }
                },
                'protectedRanges': {
                    'protectedRangeId': 0,
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    }
                },
            }
        }

        spreadsheet = sheet.create(body=spreadsheet,
                                   fields='spreadsheetId').execute()
        spreadsheet_Id = spreadsheet['spreadsheetId']

        # Add header rows
        values = [
            ["System", "GFLOPS", "GFLOP Scaling", "Cost/hr", "Price/Perf"]
        ]

        body = {
            'values': values
        }

        return sheet.values().update(spreadsheetId=spreadsheet_Id,
                                     range='A:F',
                                     valueInputOption='USER_ENTERED',
                                     body=body).execute()
    if test_name == 'stream':
        requests = {
            'addSheet': {
                'properties': {
                    'sheetId': 1,
                    'title': test_name,
                    'gridProperties': {
                        'frozenRowCount': 1,
                    }
                }
            }
        }

        body = {
            'requests': requests
        }

        try:
            response = sheet.batchUpdate(
                spreadsheetId=spreadsheet_Id, body=body).execute()
        except HttpError as error:
            print(error)


def extract_data(path):
    """
    """
    # Find and seek logic

    # data_index = 0
    # with open(path) as file:
    #     for line in file:
    #         data = file.readlines()
    #         if 'Performance Summar'

    # for x in data:
    #     if 'Performance Summary (GFlops)' in x:
    #         gflops = data[data_index+3].split()[3]
    #     index = index + 1

    with open(path) as file:
        gflops = file.readlines()[28].split()[3]

    return gflops


def append_to_sheet(sheet, spreadsheet_Id, results, range='A:F'):
    """
    """
    if range == 'stream':
        values = [
            *results
        ]
    else:
        values = [
            results
        ]

    body = {
        'values': values
    }

    response = sheet.values().append(spreadsheetId=spreadsheet_Id,
                                     range=range,
                                     valueInputOption='USER_ENTERED',
                                     body=body).execute()
    print(response)
    return response


def read_sheet(sheet, spreadsheet_Id, range='A:F'):
    """
    """
    result = sheet.values().get(spreadsheetId=spreadsheet_Id,
                                range=range).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s' % (row))


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


def main():
    """
    """
    # ToDo: Following values will be processed via parser
    test_name = 'stream'
    linpack_result_path = 'linpack/perf64.perf.lab.eng.bos.redhat.com.txt'
    stream_path = 'results_streams_tuned_tuned_virtual-guest_sys_file_none/streams_results/streams_O3_tuned_virtual-guest_sys_file_none.out'
    spreadsheet_Id = '1aUwUL99-FHfH0NdbxfGW886sqSEXVU2yVBOXAJf2RXc'
    results = ['perf64']
    cloud = 'AWS'

    creds = authenticate_creds()
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    # if spreadsheet_Id is None:
    spreadsheet = create_sheet(sheet, test_name, spreadsheet_Id)

    if test_name == 'linpack':
        gflops = extract_data(linpack_result_path)
        if cloud == 'AWS':
            price_per_hour = get_ondemand_hourly_price(
                'm5.xlarge', 'US East (N. Virginia)')

        results.append(gflops)
        results.append(1)
        results.append(price_per_hour)
        results.append(float(gflops)/float(price_per_hour))

    if test_name == 'stream':
        results = extract_stream_data(stream_path, results)

    response = append_to_sheet(sheet, spreadsheet_Id, results, test_name)
    read_sheet(sheet, spreadsheet_Id, range=test_name)


# TO:DO Add parser information here
if __name__ == '__main__':
    main()

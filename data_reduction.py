from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

from config import *
from get_aws_pricing import get_ondemand_hourly_price
from util import read_sheet, append_to_sheet, authenticate_creds
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


def main():
    """
    """
    # if spreadsheet_Id is None:
    spreadsheet = create_sheet(sheet, test_name, spreadsheet_Id)

    if test_name == 'linpack':
        results = []
        gflops = extract_data(linpack_result_path)
        if cloud == 'AWS':
            price_per_hour = get_ondemand_hourly_price(
                'm5.xlarge', 'US East (N. Virginia)')
        results.append(system_name)
        results.append(gflops)
        results.append(1)
        results.append(price_per_hour)
        results.append(float(gflops)/float(price_per_hour))

        results = [results]

    if test_name == 'stream':
        results = extract_stream_data(stream_path, system_name)

    response = append_to_sheet(sheet, spreadsheet_Id, results, test_name)


# TO:DO Add parser information here
if __name__ == '__main__':
    main()

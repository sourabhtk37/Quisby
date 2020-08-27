# TODO: scope of sheet(), var:spreadsheetId and other vars is global,
#       therefore function sizes can be reduced
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

import graph
import cloud_pricing
from util import read_sheet, append_to_sheet, authenticate_creds, get_sheet
from stream import extract_stream_data
from uperf import extract_uperf_data
from config import *


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
LINPACK_HEADER_ROW = ["System", "GFLOPS",
                      "GFLOP Scaling", "Cost/hr", "Price/Perf"]


def create_spreadsheet(sheet, spreadsheet_name, test_name):
    """
    A new sheet is created if spreadsheetId is None

    :sheet: Google sheet API function
    :name: Spreadsheet title
    """
    spreadsheet = {
        'properties': {
            'title': spreadsheet_name
        },
        'sheets': {
            'properties': {
                'sheetId': 0,
                'title': test_name,
                'gridProperties': {
                    'frozenRowCount': 1,
                }
            }
        }
    }

    spreadsheet = sheet.create(body=spreadsheet,
                               fields='spreadsheetId').execute()

    return spreadsheet['spreadsheetId']


def create_sheet(sheet, spreadsheetId, test_name, sheet_count):
    """
    New sheet in spreadsheet is created

    :sheet: Google sheet API function
    :spreadsheetId
    :test_name: range to graph up the data, it will be mostly sheet name
    """
    requests = {
        'addSheet': {
            'properties': {
                'sheetId': sheet_count + 1,
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

    sheet.batchUpdate(
        spreadsheetId=spreadsheetId, body=body).execute()

    if test_name == 'linpack':
        # Add header rows
        values = [
            LINPACK_HEADER_ROW
        ]

        body = {
            'values': values
        }

        sheet.values().update(spreadsheetId=spreadsheetId,
                              range=test_name,
                              valueInputOption='USER_ENTERED',
                              body=body).execute()


def extract_linpack_data(path):
    """
    Reads linpack results file and extract gflops information

    :path: linpack results path
    """

    results = []
    with open(path) as file:
        gflops = file.readlines()[28].split()[3]

    get_cloud_pricing = getattr(
        cloud_pricing, 'get_%s_pricing' % cloud_type.lower())
    price_per_hour = get_cloud_pricing(system_name, region)

    results.append(system_name)
    results.append(gflops)
    results.append(1)
    results.append(price_per_hour)
    results.append(float(gflops)/float(price_per_hour))

    return [results]


def check_sheet_exists(sheet_info):
    """
    """
    for sheet_prop in sheet_info:
        if test_name == sheet_prop['properties']['title']:
            return True

    return False


def main():
    """
    """
    global spreadsheetId
    sheet_exists = False

    # TODO: Need to apply to config.py afterwards, Need a way to a manage multiple
    #       spreadsheets.
    # TODO: Write the created spreadsheetId to config file
    # Create new spreadsheet if it doesn't exist
    if not spreadsheetId:
        spreadsheetId = create_spreadsheet(sheet, spreadsheet_name, test_name)

    sheet_info = get_sheet(sheet, spreadsheetId, [])['sheets']

    # Create sheet if it doesn't exit
    if not check_sheet_exists(sheet_info):
        sheet_count = len(sheet_info)
        create_sheet(
            sheet, spreadsheetId, test_name, sheet_count)

    # TODO: Remove if-else using getattr
    if test_name == 'linpack':
        # Collecting data
        results = extract_linpack_data(path)

    elif test_name == 'stream':
        results = extract_stream_data(path, system_name)

    elif test_name == 'uperf':
        results = extract_uperf_data(path, system_name)

    # Appending data to sheet
    response = append_to_sheet(sheet, spreadsheetId, results, test_name)

    # Graphing up data
    graph_process_data = getattr(graph, 'graph_%s_data' % (test_name))
    graph_process_data(sheet, spreadsheetId, test_name)


# TO:DO Add parser information here
if __name__ == '__main__':
    main()

# TODO: scope of sheet(), var:spreadsheetId and other vars is global,
#       therefore function sizes can be reduced
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

import graph
import cloud_pricing
from util import read_sheet, append_to_sheet, authenticate_creds
from stream_parse import extract_stream_data
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


def create_sheet(sheet, spreadsheetId, test_name):
    """
    New sheet in spreadsheet is created

    :sheet: Google sheet API function
    :spreadsheetId
    :test_name: range to graph up the data, it will be mostly sheet name
    """
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
            spreadsheetId=spreadsheetId, body=body).execute()
    except HttpError as error:
        print(error)

    if test_name == 'linpack':
        # Add header rows
        values = [
            LINPACK_HEADER_ROW
        ]

        body = {
            'values': values
        }

        return sheet.values().update(spreadsheetId=spreadsheetId,
                                     range=test_name,
                                     valueInputOption='USER_ENTERED',
                                     body=body).execute()


def extract_linpack_data(path):
    """
    Reads linpack results file and extract gflops information

    :path: linpack results path
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
    global spreadsheetId

    if not spreadsheetId:
        spreadsheetId = create_spreadsheet(sheet, spreadsheet_name, test_name)
    
    spreadsheet = create_sheet(sheet, spreadsheetId, test_name)

    if test_name == 'linpack':
        results = []

        # Collecting data
        gflops = extract_linpack_data(linpack_result_path)
        get_cloud_pricing = getattr(
            cloud_pricing, 'get_%s_pricing' % cloud_type.lower())
        price_per_hour = get_cloud_pricing(system_name, region)

        results.append(system_name)
        results.append(gflops)
        results.append(1)
        results.append(price_per_hour)
        results.append(float(gflops)/float(price_per_hour))

        results = [results]

    if test_name == 'stream':
        results = extract_stream_data(stream_path, system_name)

    response = append_to_sheet(sheet, spreadsheetId, results, test_name)

    # Graphing

    graph_process_data = getattr(graph, 'graph_%s_data' % (test_name))
    graph_process_data(sheet, spreadsheetId, test_name)


# TO:DO Add parser information here
if __name__ == '__main__':
    main()

# TODO: scope of sheet(), var:spreadsheetId and other vars is global,
#       therefore function sizes can be reduced
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

import graph
import cloud_pricing
from util import *
from stream import extract_stream_data
from uperf import extract_uperf_data
from config import *



def extract_linpack_data(path, system_name):
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


def main(test_name, test_path, system_name):
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
    if not check_sheet_exists(sheet_info, test_name):
        sheet_count = len(sheet_info)
        create_sheet(
            sheet, spreadsheetId, test_name, sheet_count)

    # TODO: Remove if-else using getattr
    # Collecting data
    if test_name == 'linpack':
        results = extract_linpack_data(test_path, system_name)

    elif test_name == 'stream':
        results = extract_stream_data(test_path, system_name)

    elif test_name == 'uperf':
        results = extract_uperf_data(test_path, system_name)

    # Appending data to sheet
    response = append_to_sheet(sheet, spreadsheetId, results, test_name)

    # Graphing up data
    graph_process_data = getattr(graph, 'graph_%s_data' % (test_name))
    graph_process_data(sheet, spreadsheetId, test_name)


# TO:DO Add parser information here
if __name__ == '__main__':
    main()

import config
import graph
import cloud_pricing
from stream import extract_stream_data
from uperf import extract_uperf_data
from sheetapi import sheet
from sheet_util import create_sheet, create_spreadsheet, get_sheet, append_to_sheet


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
    sheet_exists = False

    if not config.spreadsheetId:
        config.spreadsheetId = create_spreadsheet(spreadsheet_name, test_name)

    sheet_info = get_sheet(config.spreadsheetId, [])['sheets']

    # Create sheet if it doesn't exit
    if not check_sheet_exists(sheet_info, test_name):
        sheet_count = len(sheet_info)
        create_sheet(config.spreadsheetId, test_name, sheet_count)

    # TODO: Remove if-else using getattr
    # Collecting data
    if test_name == 'linpack':
        results = extract_linpack_data(test_path, system_name)

    elif test_name == 'stream':
        results = extract_stream_data(test_path, system_name)

    elif test_name == 'uperf':
        results = extract_uperf_data(test_path, system_name)

    # Appending data to sheet
    response = append_to_sheet(config.spreadsheetId, results, test_name)

    # Graphing up data
    graph_process_data = getattr(graph, 'graph_%s_data' % (test_name))
    graph_process_data(config.spreadsheetId, test_name)


# TO:DO Add parser information here
if __name__ == '__main__':
    main(test_name, test_path, system_name)

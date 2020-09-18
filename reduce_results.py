import sys

import graph
import config
from sheetapi import sheet
from stream import extract_stream_data, create_summary_stream_data
from uperf import extract_uperf_data, create_summary_uperf_data
from linpack.extract import extract_linpack_summary_data
from sheet_util import create_sheet, append_to_sheet, create_spreadsheet


def process_results(results):
    """
    """
    if results:
        if test_name == 'stream':
            results = create_summary_stream_data(results)
        elif test_name == 'uperf':
            results = create_summary_uperf_data(results)

        create_sheet(config.spreadsheetId, test_name)
        append_to_sheet(config.spreadsheetId,
                        results, test_name)

        # Graphing up data
        graph_process_data = getattr(
            graph, 'graph_%s_data' % (test_name))
        graph_process_data(config.spreadsheetId, test_name)

    return []


def data_handler(path):
    """
    """
    global test_name

    spreadsheet_name = f"{config.cloud_type} {config.OS_TYPE}-{config.OS_RELEASE} report"

    results = []

    with open(path) as file:
        test_result_path = file.readlines()

        for data in test_result_path:
            if 'tests' in data:
                results = process_results(results)
                test_name = data.split('_')[-1].strip()
                
                if not config.spreadsheetId:
                    config.spreadsheetId = create_spreadsheet(
                        spreadsheet_name, test_name)
            else:
                if data:
                    
                    # Strip new line
                    data = data.strip('\n')

                    if test_name == 'stream':
                        system_name = data.split('/')[1].strip()
                        result_name = data.split('/')[-1].strip('\n')
                        test_path = f"stream_result_{config.OS_RELEASE}/{data}" \
                                    f"/{result_name}/streams_results/" \
                                    f"{result_name}/results_streams.csv"

                        results += extract_stream_data(test_path, system_name)

                    elif test_name == 'uperf':
                        # Strip "'" from the EOL
                        data = data.strip("'")
                        system_name = data.split('_')[3].split(':')[0].strip()
                        test_path = f"uperf_results_{config.OS_RELEASE}/" \
                                    f"{data}result.csv"

                        results += extract_uperf_data(test_path, system_name)

                    elif test_name == 'linpack':
                        system_name = data.split('/')[1].strip()
                        result_name = data.split('/')[-1].strip('\n')
                        test_path = f"linpack_result_{config.OS_RELEASE}/" \
                                    f"{data}/{result_name}/summary.csv"

                        ret_val = extract_linpack_summary_data(
                            test_path, system_name)
                        if ret_val:
                            results += ret_val

        results = process_results(results)

        print(f'https://docs.google.com/spreadsheets/d/{config.spreadsheetId}')


if __name__ == '__main__':

    try:
        arg = sys.argv[1]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} <test results location file>")

    config.OS_RELEASE = arg.split('_')[-1]
    data_handler(arg)

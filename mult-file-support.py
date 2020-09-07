import csv

from stream import extract_stream_data
from uperf import extract_uperf_data
from config import *
from util import *
import graph
import cloud_pricing


def extract_linpack_data(path, system_name):
    """
    Make shift function to handle linpack summary data 
    till a resolution is reached
    """

    results = []

    with open(path) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=':')

        for row in csv_reader:
            gflops = row['MB/sec']

    if gflops:
        get_cloud_pricing = getattr(
            cloud_pricing, 'get_%s_pricing' % cloud_type.lower())
        price_per_hour = get_cloud_pricing(system_name, region)

        results.append(system_name)
        results.append(gflops)
        results.append(1)
        results.append(price_per_hour)
        results.append(float(gflops)/float(price_per_hour))

        return [results]


def data_handler(path):
    """
    """
    global spreadsheetId
    global test_name

    with open(path) as file:
        test_result_path = file.readlines()
        results = []

        for data in test_result_path:
            if 'tests' in data:

                if results:
                    create_sheet(sheet, spreadsheetId, test_name)
                    append_to_sheet(sheet, spreadsheetId,
                                    results, test_name)

                    # Graphing up data
                    graph_process_data = getattr(
                        graph, 'graph_%s_data' % (test_name))
                    graph_process_data(sheet, spreadsheetId, test_name)

                    results = []

                test_name = data.split('_')[-1].strip()

                if not spreadsheetId:
                    spreadsheetId = create_spreadsheet(
                        sheet, spreadsheet_name, test_name)

            else:
                system_name = data.split('/')[1].strip()
                result_name = data.split('/')[-1].strip('\n')

                if test_name == 'stream':

                    test_path = 'stream_result_' + OS_RELEASE + '/' + \
                        data.strip('\n') + '/' + \
                        result_name + \
                        '/streams_results/' + result_name + '/results_streams.csv'

                    results += extract_stream_data(test_path, system_name)

                elif test_name == 'uperf':
                    system_name = data.split('_')[3].split(':')[0].strip()

                    test_path = 'uperf_results_' + OS_RELEASE + '/' + \
                        data.strip('\n') + 'result.csv'

                    results += extract_uperf_data(test_path, system_name)

                elif test_name == 'linpack':
                    test_path = 'linpack_result_' + OS_RELEASE + '/' + \
                        data.strip('\n') + '/' + result_name + '/summary.csv'

                    ret_val = extract_linpack_data(test_path, system_name)
                    if ret_val:
                        results += ret_val

        if results:
            create_sheet(sheet, spreadsheetId, test_name)
            append_to_sheet(sheet, spreadsheetId,
                            results, test_name)

            # Graphing up data
            graph_process_data = getattr(
                graph, 'graph_%s_data' % (test_name))
            graph_process_data(sheet, spreadsheetId, test_name)

            results = []


if __name__ == '__main__':
    data_handler("test_locations_8.2")

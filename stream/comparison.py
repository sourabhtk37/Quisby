from itertools import groupby

import config
from sheet_util import create_spreadsheet, append_to_sheet, read_sheet, get_sheet
from util import combine_two_array_alternating
from graph import graph_stream_data


def compare_stream_results(spreadsheets, test_name, table_name=['Max Througput']):
    values = []
    results = []
    spreadsheet_name = []

    for spreadsheetId in spreadsheets:
        values.append(read_sheet(spreadsheetId, range=test_name))
        spreadsheet_name.append(get_sheet(spreadsheetId, range=[])[
                                'properties']['title'])

    spreadsheet_name = " vs ".join(spreadsheet_name)

    for index, value in enumerate(values):
        values[index] = (list(g) for k, g in groupby(
            value, key=lambda x: x != []) if k)
    list_1 = list(values[0])
    list_2 = list(values[1])

    for value in list_1:
        results.append([""])

        for ele in list_2:
            if value[0][0] in table_name and ele[0][0] in table_name:
                results = combine_two_array_alternating(results, value, ele)
                break

            elif value[1][0] == ele[1][0]:
                results.append(value[0])
                results = combine_two_array_alternating(
                    results, value[1:], ele[1:])
                break

    spreadsheetId = create_spreadsheet(spreadsheet_name, test_name)
    append_to_sheet(spreadsheetId, results, test_name)
    graph_stream_data(spreadsheetId, test_name)

    print(f'https://docs.google.com/spreadsheets/d/{spreadsheetId}')

    return results


spreadsheets = ['1sOTLWbBGvBdiYS-AYwPd6EjlH9AF47PsVQipCWQmzZE',
                '1UNt_l3a0LIw1NDyKDFyMRyVmfBc5mplBsUIYI_7jjZ4']

test_name = 'stream'
compare_stream_results(spreadsheets, test_name)

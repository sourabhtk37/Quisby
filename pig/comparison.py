from itertools import groupby

import config.config as config
from sheet_util import create_spreadsheet, append_to_sheet, read_sheet, get_sheet
from util import combine_two_array_alternating
from pig.graph import graph_pig_data
from specjbb import specjbb_sort_data_by_system_family


def compare_pig_results(spreadsheets):
    spreadsheet_name = []
    values = []
    results = []
    test_name = 'pig'

    for spreadsheetId in spreadsheets:
        values.append(read_sheet(spreadsheetId, range=test_name))
        spreadsheet_name.append(get_sheet(spreadsheetId, range=[])[
                                'properties']['title'])

    spreadsheet_name = " vs ".join(spreadsheet_name)

    for index, value in enumerate(values):
        values[index] = (list(g) for k, g in groupby(
            value, key=lambda x: x != []) if k)

    for value, ele in zip(values[0], values[1]):
        results.append([""])
        if value[0] == ele[0]:
            results.append(value[0])
            results = combine_two_array_alternating(
                results, value[1:], ele[1:])

    spreadsheetId = create_spreadsheet(spreadsheet_name, test_name)
    append_to_sheet(spreadsheetId, results, test_name)
    graph_pig_data(spreadsheetId, test_name)

    print(f'https://docs.google.com/spreadsheets/d/{spreadsheetId}')

    return results


spreadsheets = ['1WZJb6pGkmrRYD4M6TeRqOSV609702O0i1mj1ksTY4ao',
                '1NxmzU6yiWzRp3PPys8Cr7kzGLP_vutSDBqCOtSuoJ0A']


compare_pig_results(spreadsheets)

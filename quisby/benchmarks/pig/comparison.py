from itertools import groupby

import quisby.config as config
from quisby.sheet.sheet_util import create_spreadsheet, append_to_sheet, read_sheet, get_sheet
from quisby.util import combine_two_array_alternating
from quisby.pig.graph import graph_pig_data


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


spreadsheets = ['1LwRv981DCe98uqAKbnRhkaE89M6IyIOTIVd9hDs5Eg8',
                '1MNLb3RTPNQHwNRFNCB71w2ESlYyMjW74pwqNFQuKNQg']


compare_pig_results(spreadsheets)

from itertools import groupby

import config
from sheetapi import sheet
from util import create_spreadsheet, append_to_sheet, read_sheet
from graph import graph_stream_data


def combine_two_array_alternating(results, value, ele):
    for list1, list2 in zip(value, ele):
        row = [None]*(len(list1[1:])+len(list2[1:]))
        row[::2] = list1[1:]
        row[1::2] = list2[1:]
        results.append([list1[0]] + row)

    return results


def compare_stream_results(spreadsheets):
    test_name = 'stream_8.2-8.3'
    values = []
    results = []

    for spreadsheetId in spreadsheets:
        values.append(read_sheet(spreadsheetId, range='stream'))

    for index, value in enumerate(values):
        values[index] = (list(g) for k, g in groupby(
            value, key=lambda x: x != []) if k)

    for value, ele in zip(values[0], values[1]):
        results.append([""])

        if value[0][0] == 'Max Througput':
            results = combine_two_array_alternating(results, value, ele)

        elif value[1][0] == ele[1][0]:
            results.append(value[0])
            results = combine_two_array_alternating(
                results, value[1:], ele[1:])

    spreadsheetId = create_spreadsheet(
        sheet, 'Comparison 8.2 vs 8.3: STREAM', test_name)
    append_to_sheet(spreadsheetId, results, test_name)
    graph_stream_data(spreadsheetId, test_name)

    print(f'https://docs.google.com/spreadsheets/d/{spreadsheetId}')

    return results


spreadsheets = ['1ucUesKesu91NfnDvpnbsEf2SluL4_NaCHLQbIf3CH9c',
                '1GofU4KegjkniGFhZInZGoBSSUP67aaCq4Jc77MEIBEE']


compare_stream_results(spreadsheets)

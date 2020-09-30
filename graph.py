from itertools import groupby

import config
from sheetapi import sheet
from uperf import combine_uperf_data
from sheet_util import clear_sheet_charts, clear_sheet_data, append_to_sheet, read_sheet, get_sheet


# TODO: remove mention of range with test_name


def graph_linpack_data(spreadsheetId, range='A:F'):
    """
    Re-arrange data from the sheet into a dict grouped by machine name.
    The sheet data & charts are then cleared excluding the header row.
    The function then processes loops over each groups of machine and plots the
    graphs.

    Graphs:
    - GFLOP and GFLOPS scaling
    - Price/perf

    :sheet: sheet API function
    :spreadsheetId
    :range: range to graph up the data, it will be mostly sheet name
    """
    GFLOPS_PLOT_RANGE = 'B'
    PRICE_PER_PERF_RANGE = 'D'
    GRAPH_COL_INDEX = 5
    GRAPH_ROW_INDEX = 0
    data_dict = rearrange_linpack_data(spreadsheetId, range)
    header_row = data_dict[0][0]

    if data_dict:
        clear_sheet_data(spreadsheetId, range)
        clear_sheet_charts(spreadsheetId, range)
    else:
        raise Exception("Data sheet empty")

    for data in data_dict:
        machine_class = data[0][1].split('.')[0]

        response = append_to_sheet(spreadsheetId, data, range)
        updated_range = response['updates']['updatedRange']
        title, sheet_range = updated_range.split('!')
        sheet_range = sheet_range.split(':')

        # apply_named_range(spreadsheetId, machine_class, updated_range)

        sheetId = get_sheet(spreadsheetId, updated_range)[
            'sheets'][0]['properties']['sheetId']

        # GFlops & GFlops scaling graph
        requests = {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "%s : %s and %s" % (title, header_row[1], header_row[2]),
                        "basicChart": {
                            "chartType": "COMBO",
                            "legendPosition": "BOTTOM_LEGEND",
                            "axis": [
                                {
                                    "position": "BOTTOM_AXIS",
                                    "title": "%s" % (header_row[0])
                                },
                                {
                                    "position": "LEFT_AXIS",
                                    "title": "%s and %s" % (header_row[1], header_row[2])
                                }
                            ],
                            "domains": [
                                {
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": sheetId,
                                                    "startRowIndex": int(sheet_range[0][1:]) - 1,
                                                    "endRowIndex": sheet_range[1][1:],
                                                    "startColumnIndex": 0,
                                                    "endColumnIndex": 1
                                                }
                                            ]
                                        }
                                    }
                                }
                            ],
                            "series": [
                                {
                                    "series": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": sheetId,
                                                    "startRowIndex": int(sheet_range[0][1:]) - 1,
                                                    "endRowIndex": sheet_range[1][1:],
                                                    "startColumnIndex": ord(GFLOPS_PLOT_RANGE) % 65,
                                                    "endColumnIndex": ord(GFLOPS_PLOT_RANGE) % 65+1
                                                }
                                            ]
                                        }
                                    },
                                    "targetAxis": "LEFT_AXIS",
                                    "type": "COLUMN"
                                },
                                {
                                    "series": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": sheetId,
                                                    "startRowIndex": int(sheet_range[0][1:]) - 1,
                                                    "endRowIndex": sheet_range[1][1:],
                                                    "startColumnIndex": ord(GFLOPS_PLOT_RANGE) % 65+1,
                                                    "endColumnIndex": ord(GFLOPS_PLOT_RANGE) % 65+2
                                                }
                                            ]
                                        }
                                    },
                                    "targetAxis": "RIGHT_AXIS",
                                    "type": "LINE"
                                }
                            ],
                            "headerCount": 1
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": sheetId,
                                "rowIndex": GRAPH_ROW_INDEX,
                                "columnIndex": ord(sheet_range[1][:1]) % 65 + 2
                            }
                        }
                    }
                }
            }
        }

        # PRICE/PERF graph
        body = {
            "requests": requests
        }

        sheet.batchUpdate(
            spreadsheetId=spreadsheetId, body=body).execute()

        requests = {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "%s : %s " % (title, header_row[4]),
                        "basicChart": {
                            "chartType": "COLUMN",
                            "legendPosition": "BOTTOM_LEGEND",
                            "axis": [
                                {
                                    "position": "BOTTOM_AXIS",
                                    "title": "%s" % (header_row[0])
                                },
                                {
                                    "position": "LEFT_AXIS",
                                    "title": "%s " % (header_row[4])
                                }
                            ],
                            "domains": [
                                {
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": sheetId,
                                                    "startRowIndex": int(sheet_range[0][1:]) - 1,
                                                    "endRowIndex": sheet_range[1][1:],
                                                    "startColumnIndex": 0,
                                                    "endColumnIndex": 1
                                                }
                                            ]
                                        }
                                    }
                                }
                            ],
                            "series": [
                                {
                                    "series": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": sheetId,
                                                    "startRowIndex": int(sheet_range[0][1:]) - 1,
                                                    "endRowIndex": sheet_range[1][1:],
                                                    "startColumnIndex": ord(PRICE_PER_PERF_RANGE) % 65,
                                                    "endColumnIndex": ord(PRICE_PER_PERF_RANGE) % 65+1
                                                }
                                            ]
                                        }
                                    },
                                    "targetAxis": "LEFT_AXIS",
                                    "type": "COLUMN"
                                }
                            ],
                            "headerCount": 1
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": sheetId,
                                "rowIndex": GRAPH_ROW_INDEX,
                                "columnIndex": ord(sheet_range[1][:1]) % 65 + 8
                            }
                        }
                    }
                }
            }
        }

        body = {
            "requests": requests
        }

        sheet.batchUpdate(
            spreadsheetId=spreadsheetId, body=body).execute()

        GRAPH_ROW_INDEX += 20


def rearrange_linpack_data(spreadsheetId, range='A:F'):
    """
    Retreived data is sorted into groups by machine name

    :sheet: sheet API function
    :spreadsheetId
    :range: range to graph up the data, it will be mostly sheet name
    """
    sorted_result = []

    values = read_sheet(spreadsheetId, range=range)

    # Clear empty rows
    values = list(filter(None, values))
    header_row = [values[0]]
    # Pop Header row to sort by system size
    values = [row for row in values if row[0] != 'System']

    for _, items in groupby(values, key=lambda x: x[0].split('.')[0]):
        sorted_data = sorted(list(items), key=lambda x: int(
            x[0].split('.')[1].split('x')[0]))

        sorted_result.append(header_row + sorted_data)

    return sorted_result


def create_series_range_list_stream(column_index, len_of_func, sheetId, start_index, end_index):
    series = []

    for index in range(len_of_func):

        series.append({
            "series": {
                "sourceRange": {
                    "sources": [
                        {
                            "sheetId": sheetId,
                            "startRowIndex": start_index,
                            "endRowIndex": end_index,
                            "startColumnIndex": column_index,
                            "endColumnIndex": column_index+1

                        }
                    ]
                }
            },
            "type": "COLUMN"
        })
        column_index += 1

    return series, column_index


def graph_stream_data(spreadsheetId, test_name):
    """
    Retreive each streams results and graph them up indvidually

    :sheet: sheet API function
    :spreadsheetId
    :test_name: test_name to graph up the data, it will be mostly sheet name
    """
    GRAPH_COL_INDEX = 0
    GRAPH_ROW_INDEX = 0
    start_index = 0
    end_index = 0

    data = read_sheet(spreadsheetId, test_name)
    clear_sheet_charts(spreadsheetId, test_name)

    for index, row in enumerate(data):
        if 'Max Througput' in row:
            start_index = index

        if start_index:
            if row == []:
                end_index = index
            if index+1 == len(data):
                end_index = index + 1

        if end_index:
            graph_data = data[start_index:end_index]
            column_count = len(graph_data[0])

            for _, items in groupby(graph_data[0][1:], key=lambda x: x.split('-')[0]):
                len_of_func = len(list(items))
                break
            column = 1
            for _ in range(column_count):
                if column >= column_count:
                    break
                sheetId = get_sheet(spreadsheetId, test_name)[
                    'sheets'][0]['properties']['sheetId']
                    
                series, column = create_series_range_list_stream(
                    column, len_of_func, sheetId, start_index, end_index)

                requests = {
                    "addChart": {
                        "chart": {
                            "spec": {
                                "title": "%s: %s" % (test_name, graph_data[0][0]),
                                "subtitle": f"{graph_data[1][0].split('.')[0]}",
                                "basicChart": {
                                    "chartType": "COLUMN",
                                    "legendPosition": "BOTTOM_LEGEND",
                                    "axis": [
                                        {
                                            "position": "BOTTOM_AXIS",
                                            "title": ""
                                        },
                                        {
                                            "position": "LEFT_AXIS",
                                            "title": "Throughput (MB/s)"
                                        }
                                    ],
                                    "domains": [
                                        {
                                            "domain": {
                                                "sourceRange": {
                                                    "sources": [
                                                        {
                                                            "sheetId": sheetId,
                                                            "startRowIndex": start_index,
                                                            "endRowIndex": end_index,
                                                            "startColumnIndex": 0,
                                                            "endColumnIndex": 1
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    ],
                                    "series": series,
                                    "headerCount": 1
                                }
                            },
                            "position": {
                                "overlayPosition": {
                                    "anchorCell": {
                                        "sheetId": sheetId,
                                        "rowIndex": GRAPH_ROW_INDEX,
                                        "columnIndex": column_count + GRAPH_COL_INDEX
                                    }
                                }
                            }
                        }
                    }
                }

                if GRAPH_COL_INDEX >= 5:
                    GRAPH_ROW_INDEX += 20
                    GRAPH_COL_INDEX = 0
                else:
                    GRAPH_COL_INDEX += 6

                body = {
                    "requests": requests
                }

                sheet.batchUpdate(
                    spreadsheetId=spreadsheetId, body=body).execute()

            # Reset variables
            start_index, end_index = 0, 0


def series_range_uperf(column_count, sheetId, start_index, end_index):

    series = []

    for index in range(column_count):

        series.append({
            "series": {
                "sourceRange": {
                    "sources": [
                        {
                            "sheetId": sheetId,
                            "startRowIndex": start_index+1,
                            "endRowIndex": end_index,
                            "startColumnIndex": index+1,
                            "endColumnIndex": index+2
                        }
                    ]
                }
            },
            "type": "COLUMN"
        })

    return series


def graph_uperf_data(spreadsheetId, range):
    """
    """
    GRAPH_COL_INDEX, GRAPH_ROW_INDEX = 2, 0
    start_index, end_index = 0, 0
    measurement = {
        'Gb_sec': 'Bandwidth',
        'trans_sec': 'Transactions/second',
        'usec': 'Latency'
    }

    uperf_results = read_sheet(spreadsheetId, range)
    clear_sheet_charts(spreadsheetId, range)

    for index, row in enumerate(uperf_results):
        if row:
            if 'tcp_stream16' in row[1] or 'tcp_rr64' in row[1]:
                start_index = index

        if start_index:
            if row == []:
                end_index = index
            if index+1 == len(uperf_results):
                end_index = index + 1

        if end_index:
            graph_data = uperf_results[start_index:end_index]
            column_count = len(uperf_results[2])

            sheetId = get_sheet(spreadsheetId, range)[
                'sheets'][0]['properties']['sheetId']

            requests = {
                "addChart": {
                    "chart": {
                        "spec": {
                            "title": f"Uperf : {measurement[graph_data[0][2]]} | {graph_data[0][1]}",
                            "subtitle": f"{graph_data[0][0]}",
                            "basicChart": {
                                "chartType": "COLUMN",
                                "legendPosition": "BOTTOM_LEGEND",
                                "axis": [
                                    {
                                        "position": "BOTTOM_AXIS",
                                        "title": "Instance count"
                                    },
                                    {
                                        "position": "LEFT_AXIS",
                                        "title": f"{graph_data[0][2]}"
                                    }
                                ],
                                "domains": [
                                    {
                                        "domain": {
                                            "sourceRange": {
                                                "sources": [
                                                    {
                                                        "sheetId": sheetId,
                                                        "startRowIndex": start_index+1,
                                                        "endRowIndex": end_index,
                                                        "startColumnIndex": 0,
                                                        "endColumnIndex": 1
                                                    }
                                                ]
                                            }
                                        }
                                    }
                                ],
                                "series": series_range_uperf(column_count, sheetId, start_index, end_index),
                                "headerCount": 1
                            }
                        },
                        "position": {
                            "overlayPosition": {
                                "anchorCell": {
                                    "sheetId": sheetId,
                                    "rowIndex": GRAPH_ROW_INDEX,
                                    "columnIndex": column_count + GRAPH_COL_INDEX
                                }
                            }
                        }
                    }
                }
            }

            if GRAPH_COL_INDEX >= 5:
                GRAPH_ROW_INDEX += 20
                GRAPH_COL_INDEX = 2
            else:
                GRAPH_COL_INDEX += 6

            body = {
                "requests": requests
            }

            sheet.batchUpdate(
                spreadsheetId=spreadsheetId, body=body).execute()

            # Reset variables
            start_index, end_index = 0, 0


def create_series_range_list_specjbb(column_count, sheetId, start_index, end_index):
    series = []

    for index in range(column_count):

        series.append({
            "series": {
                "sourceRange": {
                    "sources": [
                        {
                            "sheetId": sheetId,
                            "startRowIndex": start_index,
                            "endRowIndex": end_index,
                            "startColumnIndex": index + 1,
                            "endColumnIndex": index + 2

                        }
                    ]
                }
            },
            "type": "COLUMN"
        })

    return series


def graph_specjbb_data(spreadsheetId, range):
    GRAPH_COL_INDEX = 1
    GRAPH_ROW_INDEX = 0
    start_index = 0
    end_index = 0

    data = read_sheet(spreadsheetId, range)
    clear_sheet_charts(spreadsheetId, range)

    for index, row in enumerate(data):
        if 'Peak' in row or 'Peak/$eff' in row:
            start_index = index

        if start_index:
            if row == []:
                end_index = index
            if index+1 == len(data):
                end_index = index + 1

        if end_index:
            graph_data = data[start_index:end_index]
            column_count = len(graph_data[0])

            sheetId = get_sheet(spreadsheetId, range)[
                'sheets'][0]['properties']['sheetId']

            requests = {
                "addChart": {
                    "chart": {
                        "spec": {
                            "title": "%s : %s" % (range, graph_data[0][0]),
                            "subtitle": f"{graph_data[1][0].split('.')[0]}",
                            "basicChart": {
                                "chartType": "COLUMN",
                                "legendPosition": "BOTTOM_LEGEND",
                                "axis": [
                                    {
                                        "position": "BOTTOM_AXIS",
                                        "title": ""
                                    },
                                    {
                                        "position": "LEFT_AXIS",
                                        "title": "Throughput (bops)"
                                    }
                                ],
                                "domains": [
                                    {
                                        "domain": {
                                            "sourceRange": {
                                                "sources": [
                                                    {
                                                        "sheetId": sheetId,
                                                        "startRowIndex": start_index,
                                                        "endRowIndex": end_index,
                                                        "startColumnIndex": 0,
                                                        "endColumnIndex": 1
                                                    }
                                                ]
                                            }
                                        }
                                    }
                                ],
                                "series": create_series_range_list_specjbb(column_count, sheetId, start_index, end_index),
                                "headerCount": 1
                            }
                        },
                        "position": {
                            "overlayPosition": {
                                "anchorCell": {
                                    "sheetId": sheetId,
                                    "rowIndex": GRAPH_ROW_INDEX,
                                    "columnIndex": column_count + GRAPH_COL_INDEX
                                }
                            }
                        }
                    }
                }
            }

            if GRAPH_COL_INDEX >= 5:
                GRAPH_ROW_INDEX += 20
                GRAPH_COL_INDEX = 1
            else:
                GRAPH_COL_INDEX += 6

            body = {
                "requests": requests
            }

            sheet.batchUpdate(
                spreadsheetId=spreadsheetId, body=body).execute()

            # Reset variables
            start_index, end_index = 0, 0


if __name__ == '__main__':
    test_name = 'uperf'

    config.spreadsheetId = '1J1nWs7TKQyYINYFklX16WQME3Dba3x46sJVxZnCjRfo'

    globals()["graph_%s_data" % (test_name)](config.spreadsheetId, test_name)

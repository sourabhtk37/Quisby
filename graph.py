from config import *
from util import *


GFLOPS_PLOT_RANGE = 'B'
PRICE_PER_PERF_RANGE = 'E'

# TODO: remove mention of range with test_name


def graph_linpack_data(sheet, spreadsheetId, range='A:F'):
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
    GRAPH_COL_INDEX = 5
    GRAPH_ROW_INDEX = 0
    
    data_dict = rearrange_linpack_data(sheet, spreadsheetId, test_name)
    header_row = data_dict[0][0]

    if data_dict:
        clear_sheet_data(sheet, spreadsheetId, range)
        clear_sheet_charts(sheet, spreadsheetId, range)
    else:
        raise Exception("Data sheet empty")

    for data in data_dict:
        machine_class = data[0][1].split('.')[0]

        response = append_to_sheet(sheet, spreadsheetId, data, test_name)
        updated_range = response['updates']['updatedRange']
        title, sheet_range = updated_range.split('!')
        sheet_range = sheet_range.split(':')

        # apply_named_range(sheet, spreadsheetId, machine_class, updated_range)

        sheetId = get_sheet(sheet, spreadsheetId, updated_range)[
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


def rearrange_linpack_data(sheet, spreadsheetId, range='A:F'):
    """
    Retreived data is sorted into groups by machine name

    :sheet: sheet API function
    :spreadsheetId
    :range: range to graph up the data, it will be mostly sheet name
    """
    values = read_sheet(sheet, spreadsheetId, range=test_name)

    data_dict = {}

    # Clear empty rows
    values = list(filter(None, values))

    for row in values:
        key = row[0].split('.')[0]

        # if row is header row, then skip
        if key == 'System':
            continue

        if cloud_type == 'AWS':
            if key in data_dict:
                data_dict[row[0].split('.')[0]] += [row]
            else:
                # Append header row and then append values to new dict
                data_dict[row[0].split('.')[0]] = [values[0]]
                data_dict[row[0].split('.')[0]] += [row]

    return list(data_dict.values())


def graph_stream_data(sheet, spreadsheetId, range):
    """
    Retreive each streams results and graph them up indvidually

    :sheet: sheet API function
    :spreadsheetId
    :range: range to graph up the data, it will be mostly sheet name
    """
    GRAPH_COL_INDEX = 5
    GRAPH_ROW_INDEX = 0

    data = read_sheet(sheet, spreadsheetId, range)
    clear_sheet_charts(sheet, spreadsheetId, range)

    for index, x in enumerate(data):
        if x == []:
            graph_data = data[index+1:index+7]
            sheetId = get_sheet(sheet, spreadsheetId, range)[
                'sheets'][0]['properties']['sheetId']
            requests = {
                "addChart": {
                    "chart": {
                        "spec": {
                            "title": "Streams : %s, System name:%s" % (graph_data[0], graph_data[1][0]),
                            "basicChart": {
                                "chartType": "COLUMN",
                                "legendPosition": "BOTTOM_LEGEND",
                                "axis": [
                                    {
                                        "position": "BOTTOM_AXIS",
                                        "title": "Function"
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
                                                        "startRowIndex": index+2,
                                                        "endRowIndex": index+7,
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
                                                        "startRowIndex": index+2,
                                                        "endRowIndex": index+7,
                                                        "startColumnIndex": 1,
                                                        "endColumnIndex": 2
                                                    }
                                                ]
                                            }
                                        },
                                        "type": "COLUMN"
                                    },
                                    {
                                        "series": {
                                            "sourceRange": {
                                                "sources": [
                                                    {
                                                        "sheetId": sheetId,
                                                        "startRowIndex": index+2,
                                                        "endRowIndex": index+7,
                                                        "startColumnIndex": 2,
                                                        "endColumnIndex": 3
                                                    }
                                                ]
                                            }
                                        },
                                        "type": "COLUMN"
                                    },
                                    {
                                        "series": {
                                            "sourceRange": {
                                                "sources": [
                                                    {
                                                        "sheetId": sheetId,
                                                        "startRowIndex": index+2,
                                                        "endRowIndex": index+7,
                                                        "startColumnIndex": 3,
                                                        "endColumnIndex": 4
                                                    }
                                                ]
                                            }
                                        },
                                        "type": "COLUMN"
                                    },
                                    {
                                        "series": {
                                            "sourceRange": {
                                                "sources": [
                                                    {
                                                        "sheetId": sheetId,
                                                        "startRowIndex": index+2,
                                                        "endRowIndex": index+7,
                                                        "startColumnIndex": 4,
                                                        "endColumnIndex": 5
                                                    }
                                                ]
                                            }
                                        },
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
                                    "columnIndex": GRAPH_COL_INDEX}
                            }
                        }
                    }
                }
            }

            if GRAPH_COL_INDEX >= 15:
                GRAPH_ROW_INDEX += 20
                GRAPH_COL_INDEX = 5
            else:
                GRAPH_COL_INDEX += 6

            body = {
                "requests": requests
            }

            sheet.batchUpdate(
                spreadsheetId=spreadsheetId, body=body).execute()


def series_range_uperf(series_range, sheetId, index, data_index):
    """
    """
    series_list = []
    GRAPH_TYPE = 'COLUMN'
    TARGET_AXIS = 'LEFT_AXIS'

    for column in range(series_range[index][0]):
        if column == 5 and series_range[index][1] > 1:
            GRAPH_TYPE = 'LINE'
            TARGET_AXIS = 'RIGHT_AXIS'

        series_list.append({
            "series": {
                "sourceRange": {
                    "sources": [
                        {
                            "sheetId": sheetId,
                            "startRowIndex": data_index[0],
                            "endRowIndex": data_index[1],
                            "startColumnIndex": column+1,
                            "endColumnIndex": column+2
                        }
                    ]
                }
            },
            "targetAxis": TARGET_AXIS,
            "type": GRAPH_TYPE
        },
        )
    return series_list


def graph_uperf_data(sheet, spreadsheetId, range):
    """
    """
    GRAPH_COL_INDEX = 6
    GRAPH_ROW_INDEX = 0

    uperf_result = read_sheet(sheet, spreadsheetId, range)
    clear_sheet_charts(sheet, spreadsheetId, range)

    loc, test_name, system_name, test_metric, series_range = [], [], [], [], []
    start_index = None
    for index, data in enumerate(uperf_result):
        if data == []:
            system_name.append(uperf_result[index+1])
            test_name.append(uperf_result[index+2])
            if start_index is not None:
                loc.append([start_index, index])
                start_index = None
            continue

        if 'instance count' in data:
            test_metric.append(set(data[1:]))

            series_range.append([len(data[1:]), len(test_metric[-1])])
            start_index = index
            continue

        if index + 2 > len(uperf_result):
            loc.append([start_index, index+1])
            start_index = None

    for index, data_index in enumerate(loc):

        sheetId = get_sheet(sheet, spreadsheetId, range)[
            'sheets'][0]['properties']['sheetId']

        requests = {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "%s , %s" % (test_name[index][0].strip("\n"), system_name[index][0]),
                        "basicChart": {
                            "chartType": "COMBO",
                            "legendPosition": "BOTTOM_LEGEND",
                            "axis": [
                                {
                                    "position": "BOTTOM_AXIS",
                                    "title": "Packet Size: %s " % (uperf_result[data_index[0]-1][0].split('-')[1])
                                },
                                {
                                    "position": "LEFT_AXIS",
                                    "title": "%s" % (",".join(test_metric[index]))
                                }
                            ],
                            "domains": [
                                {
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": sheetId,
                                                    "startRowIndex": data_index[0],
                                                    "endRowIndex": data_index[1],
                                                    "startColumnIndex": 0,
                                                    "endColumnIndex": 1
                                                }
                                            ]
                                        }
                                    }
                                },
                            ],
                            # TODO: Create a series dict according to number of series
                            "series": series_range_uperf(series_range, sheetId, index, data_index),
                            "headerCount": 1
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": sheetId,
                                "rowIndex": GRAPH_ROW_INDEX,
                                "columnIndex": GRAPH_COL_INDEX
                            }
                        }
                    }
                }
            }
        }

        if GRAPH_COL_INDEX >= 15:
            GRAPH_ROW_INDEX += 18
            GRAPH_COL_INDEX = 6
        else:
            GRAPH_COL_INDEX += 6

        body = {
            "requests": requests
        }

        sheet.batchUpdate(
            spreadsheetId=spreadsheetId, body=body).execute()


if __name__ == '__main__':
    test_name = 'uperf'
    cloud_type = 'AWS'
    creds = authenticate_creds()
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    spreadsheetId = '1aUwUL99-FHfH0NdbxfGW886sqSEXVU2yVBOXAJf2RXc'

    globals()["graph_%s_data" % (test_name)](sheet, spreadsheetId, test_name)

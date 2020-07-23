from config import *
from util import *


GFLOPS_PLOT_RANGE = 'B'


def graph_linpack_data(sheet, spreadsheetId, range='A:F'):

    data_dict = rearrange_linpack_data(sheet, spreadsheetId, test_name)
    header_row = data_dict[0][0]

    if data_dict:
        clear_sheet_data(sheet, spreadsheetId, range)
        clear_sheet_charts(sheet, spreadsheetId, range)
    else:
        raise Exception("Data sheet empty")

    for data in data_dict[1:]:
        machine_class = data[0][0].split('.')[0]

        response = append_to_sheet(sheet, spreadsheetId, data, test_name)

        updated_range = response['updates']['updatedRange']

        # apply_named_range(sheet, spreadsheetId, machine_class, updated_range)

        sheetId = get_sheet(sheet, spreadsheetId, updated_range)[
            'sheets'][0]['properties']['sheetId']

        title, sheet_range = updated_range.split('!')
        sheet_range = sheet_range.split(':')

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
                            ]
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": sheetId,
                                "rowIndex": int(sheet_range[0][1:]) - 1,
                                "columnIndex": ord(sheet_range[1][:1]) % 65 + 2
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


def rearrange_linpack_data(sheet, spreadsheetId, range='A:F'):
    """
    For linpack
    """
    values = read_sheet(sheet, spreadsheetId, range=test_name)

    data_dict = {}

    # Clear empty rows
    values = list(filter(None, values))

    for row in values[1:]:
        key = row[0].split('.')[0]
        if cloud_type == 'AWS':
            if key in data_dict:
                data_dict[row[0].split('.')[0]] += [row]
            else:
                data_dict[row[0].split('.')[0]] = [row]

    return [[values[0]]] + list(data_dict.values())


def graph_stream_data(sheet, spreadsheetId, range):
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
                                                        "startRowIndex": index+3,
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
                                                        "startRowIndex": index+3,
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
                                                        "startRowIndex": index+3,
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
                                                        "startRowIndex": index+3,
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
                                                        "startRowIndex": index+3,
                                                        "endRowIndex": index+7,
                                                        "startColumnIndex": 4,
                                                        "endColumnIndex": 5
                                                    }
                                                ]
                                            }
                                        },
                                        "type": "COLUMN"
                                    }
                                ]
                            }
                        },
                        "position": {
                            "overlayPosition": {
                                "anchorCell": {
                                    "sheetId": sheetId,
                                    "rowIndex": index,
                                    "columnIndex": 6
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


if __name__ == '__main__':
    test_name = 'linpack'
    cloud_type = 'AWS'
    creds = authenticate_creds()
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    spreadsheetId = '1aUwUL99-FHfH0NdbxfGW886sqSEXVU2yVBOXAJf2RXc'

    graph_linpack_data(sheet, spreadsheetId, test_name)
    graph_stream_data(sheet, spreadsheetId, test_name)

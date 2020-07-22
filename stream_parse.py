from operator import itemgetter

from util import read_sheet, authenticate_creds
from graph_data import clear_sheet_charts, get_sheet

from config import *


def extract_stream_data(path, system_name='System'):
    """
    Extracts streams data and takes average of multiple iterations
    """

    with open(path) as file:
        streams_results = file.readlines()

    # Streams data is sorted by socket number
    data_index = 0
    for index, data in enumerate(streams_results):
        if 'buffer size' in data:
            data_index = index
        streams_results[index] = data.strip('\n').split(':')

    streams_results = sorted(
        streams_results[data_index+1:], key=itemgetter(2))

    # A list of list is created which has format
    # [[''], ['<Socket number>'], [system_name], [<COPY data>],
    # [<SCALE data>], [<ADD data>], [<TRIAD data>]]

    socket_number = ''
    proccessed_data = []
    for x in streams_results:
        if socket_number != x[2]:
            socket_number = x[2]
            proccessed_data += [''], ['%s Socket' % x[2]], [system_name], [
                'Copy'], ['Scale'], ['Add'], ['Triad']

        # Appending copy, scale, add and triad data
        pos = len(proccessed_data)
        pos_line = len(x)
        proccessed_data[pos - 5].append(x[0])
        for i in range(1, 5):
            proccessed_data[pos-i].append(x[pos_line-i])

    return proccessed_data


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
    graph_stream_data(sheet, spreadsheetId, test_name)

import quisby.config as config
from quisby.sheet.sheetapi import sheet
from quisby.sheet.sheet_util import read_sheet, create_spreadsheet, append_to_sheet, clear_sheet_charts, clear_sheet_data, get_sheet
from quisby.benchmarks.linpack.graph import rearrange_linpack_data


def graph_linpack_comparison(spreadsheetId, range='A:F'):
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
    PRICE_PER_PERF_RANGE = 'H'
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

        # apply_named_range(sheet, spreadsheetId, machine_class, updated_range)

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
                                    "title": "%s, %s and %s, %s " % (header_row[1], header_row[2], header_row[4], header_row[5])
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
                                                    "startColumnIndex": ord(GFLOPS_PLOT_RANGE) % 65+3,
                                                    "endColumnIndex": ord(GFLOPS_PLOT_RANGE) % 65+4
                                                }
                                            ]
                                        }
                                    },
                                    "targetAxis": "RIGHT_AXIS",
                                    "type": "LINE"
                                },
                                {
                                    "series": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": sheetId,
                                                    "startRowIndex": int(sheet_range[0][1:]) - 1,
                                                    "endRowIndex": sheet_range[1][1:],
                                                    "startColumnIndex": ord(GFLOPS_PLOT_RANGE) % 65+4,
                                                    "endColumnIndex": ord(GFLOPS_PLOT_RANGE) % 65+5
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
                        "title": "%s : Price/Perf " % (title),
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
                                    "title": "GFlops/$/hr "
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
                                },
                                {
                                    "series": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": sheetId,
                                                    "startRowIndex": int(sheet_range[0][1:]) - 1,
                                                    "endRowIndex": sheet_range[1][1:],
                                                    "startColumnIndex": ord(PRICE_PER_PERF_RANGE) % 65+1,
                                                    "endColumnIndex": ord(PRICE_PER_PERF_RANGE) % 65+2
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

# TODO: Accomodate multiple release comparison


def compare_linpack_results(spreadsheets):
    values = []
    results = []
    test_name = 'linpack_8.2-8.3'

    for spreadsheetId in spreadsheets:
        values.append(read_sheet(spreadsheetId, range='linpack'))

    for v in values[0]:
        if v[0] == 'System':
            results.append(['System', 'GFLOPS - 8.2', 'GFLOPS - 8.3', '% Diff', 'GFLOP Scaling - 8.2', 'GFLOP Scaling - 8.3',
                            'Cost / hr', 'Price/Perf - 8.2', 'Price/Perf - 8.3', 'Price/Perf % Diff'])
        for y in values[1]:
            if y[0] == 'System':
                continue
            if v[0] in y[0]:
                price_perf = []
                perc_diff = (float(y[1]) - float(v[1]))/float(v[1])

                price_perf.append(float(v[1])/float(v[3]))
                price_perf.append(float(y[1])/float(y[3]))

                price_perf_diff = (
                    float(price_perf[1]) - float(price_perf[0])) / float(price_perf[0])

                results.append([v[0], v[1], y[1], perc_diff, v[2], y[2],
                                v[3], price_perf[0], price_perf[1], price_perf_diff])

    spreadsheetId = create_spreadsheet('Comparison 8.2 vs 8.3', test_name)
    append_to_sheet(spreadsheetId, results, range=test_name)
    graph_linpack_comparison(spreadsheetId, range=test_name)

    print(f'https://docs.google.com/spreadsheets/d/{spreadsheetId}')


spreadsheets = ['1lJUGyD1ca4vsTkUYRpW8CkFq15ABWdhqxyJMGDImKu0',
                '1Mq6U3hZrKOc-m_8-ufOwX1Md5ooTjPMa30aZSjDUwkA']
compare_linpack_results(spreadsheets)

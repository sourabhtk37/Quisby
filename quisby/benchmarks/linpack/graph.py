from itertools import groupby

import quisby.config as config
from quisby.sheet.sheetapi import sheet
from quisby.sheet.sheet_util import (
    clear_sheet_charts,
    clear_sheet_data,
    append_to_sheet,
    read_sheet,
    get_sheet,
)


# TODO: remove mention of range with test_name


def rearrange_linpack_data(spreadsheetId, range="A:F"):
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
    values = [row for row in values if row[0] != "System"]

    for _, items in groupby(values, key=lambda x: x[0].split(".")[0]):
        sorted_data = sorted(
            list(items), key=lambda x: int(x[0].split(".")[1].split("x")[0])
        )

        sorted_result.append(header_row + sorted_data)

    return sorted_result


def graph_linpack_data(spreadsheetId, range="A:F"):
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
    GFLOPS_PLOT_RANGE = "B"
    PRICE_PER_PERF_RANGE = "D"
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
        machine_class = data[0][1].split(".")[0]

        response = append_to_sheet(spreadsheetId, data, range)
        updated_range = response["updates"]["updatedRange"]
        title, sheet_range = updated_range.split("!")
        sheet_range = sheet_range.split(":")

        # apply_named_range(spreadsheetId, machine_class, updated_range)

        sheetId = get_sheet(spreadsheetId, updated_range)["sheets"][0]["properties"][
            "sheetId"
        ]

        # GFlops & GFlops scaling graph
        requests = {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "%s : %s and %s"
                        % (title, header_row[1], header_row[2]),
                        "basicChart": {
                            "chartType": "COMBO",
                            "legendPosition": "BOTTOM_LEGEND",
                            "axis": [
                                {
                                    "position": "BOTTOM_AXIS",
                                    "title": "%s" % (header_row[0]),
                                },
                                {
                                    "position": "LEFT_AXIS",
                                    "title": "%s and %s"
                                    % (header_row[1], header_row[2]),
                                },
                            ],
                            "domains": [
                                {
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": sheetId,
                                                    "startRowIndex": int(
                                                        sheet_range[0][1:]
                                                    )
                                                    - 1,
                                                    "endRowIndex": sheet_range[1][1:],
                                                    "startColumnIndex": 0,
                                                    "endColumnIndex": 1,
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
                                                    "startRowIndex": int(
                                                        sheet_range[0][1:]
                                                    )
                                                    - 1,
                                                    "endRowIndex": sheet_range[1][1:],
                                                    "startColumnIndex": ord(
                                                        GFLOPS_PLOT_RANGE
                                                    )
                                                    % 65,
                                                    "endColumnIndex": ord(
                                                        GFLOPS_PLOT_RANGE
                                                    )
                                                    % 65
                                                    + 1,
                                                }
                                            ]
                                        }
                                    },
                                    "targetAxis": "LEFT_AXIS",
                                    "type": "COLUMN",
                                },
                                {
                                    "series": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": sheetId,
                                                    "startRowIndex": int(
                                                        sheet_range[0][1:]
                                                    )
                                                    - 1,
                                                    "endRowIndex": sheet_range[1][1:],
                                                    "startColumnIndex": ord(
                                                        GFLOPS_PLOT_RANGE
                                                    )
                                                    % 65
                                                    + 1,
                                                    "endColumnIndex": ord(
                                                        GFLOPS_PLOT_RANGE
                                                    )
                                                    % 65
                                                    + 2,
                                                }
                                            ]
                                        }
                                    },
                                    "targetAxis": "RIGHT_AXIS",
                                    "type": "LINE",
                                },
                            ],
                            "headerCount": 1,
                        },
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": sheetId,
                                "rowIndex": GRAPH_ROW_INDEX,
                                "columnIndex": ord(sheet_range[1][:1]) % 65 + 2,
                            }
                        }
                    },
                }
            }
        }

        # PRICE/PERF graph
        body = {"requests": requests}

        sheet.batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()

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
                                    "title": "%s" % (header_row[0]),
                                },
                                {
                                    "position": "LEFT_AXIS",
                                    "title": "%s " % (header_row[4]),
                                },
                            ],
                            "domains": [
                                {
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": sheetId,
                                                    "startRowIndex": int(
                                                        sheet_range[0][1:]
                                                    )
                                                    - 1,
                                                    "endRowIndex": sheet_range[1][1:],
                                                    "startColumnIndex": 0,
                                                    "endColumnIndex": 1,
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
                                                    "startRowIndex": int(
                                                        sheet_range[0][1:]
                                                    )
                                                    - 1,
                                                    "endRowIndex": sheet_range[1][1:],
                                                    "startColumnIndex": ord(
                                                        PRICE_PER_PERF_RANGE
                                                    )
                                                    % 65,
                                                    "endColumnIndex": ord(
                                                        PRICE_PER_PERF_RANGE
                                                    )
                                                    % 65
                                                    + 1,
                                                }
                                            ]
                                        }
                                    },
                                    "targetAxis": "LEFT_AXIS",
                                    "type": "COLUMN",
                                }
                            ],
                            "headerCount": 1,
                        },
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": sheetId,
                                "rowIndex": GRAPH_ROW_INDEX,
                                "columnIndex": ord(sheet_range[1][:1]) % 65 + 8,
                            }
                        }
                    },
                }
            }
        }

        body = {"requests": requests}

        sheet.batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()

        GRAPH_ROW_INDEX += 20

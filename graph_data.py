import pprint

from config import *
from util import read_sheet, authenticate_creds

GFLOPS_PLOT_RANGE = 'B'
pp = pprint.PrettyPrinter(indent=4)


def get_named_range(sheet, spreadsheetId, range='A:F'):
    spreadsheet = get_sheet(sheet, spreadsheetId, range)

    # print(spreadsheet['namedRanges'])


def graph_data(sheet, spreadsheetId, range='A:F'):
    sheetId = get_sheet(sheet, spreadsheetId, range)[
        'sheets'][0]['properties']['sheetId']

    header_row = read_sheet(sheet, spreadsheetId, range='A1:C1')[0]

    title, sheet_range = range.split('!')
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


def apply_named_range(sheet, spreadsheetId, name, range='A:F'):

    sheetId = get_sheet(sheet, spreadsheetId, range)[
        'sheets'][0]['properties']['sheetId']

    sheet_range = range.split('!')[1].split(':')

    body = {
        "requests": [{
            "addNamedRange": {
                "namedRange": {
                    "namedRangeId": range,
                    "name": name+"_NR",
                    "range": {
                        "sheetId": sheetId,
                        "startRowIndex": int(sheet_range[0][1:]) - 1,
                        "endRowIndex": sheet_range[1][1:],
                        "startColumnIndex": ord(sheet_range[0][:1]) % 65,
                        "endColumnIndex": ord(sheet_range[1][:1]) % 65 + 1
                    }
                }
            },
        }
        ]
    }

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheetId, body=body).execute()

    print(response)


def get_sheet(sheet, spreadsheetId, range='A:F'):

    return sheet.get(spreadsheetId=spreadsheetId,
                     ranges=range).execute()


def clear_sheet_data(sheet, spreadsheetId, range='A2:Z1000'):
    # Clear values
    sheet.values().clear(spreadsheetId=spreadsheetId,
                         range='A2:Z1000', body={}).execute()


def clear_sheet_charts(sheet, spreadsheetId, range='A2:Z1000'):
    # Clear charts
    sheet_properties = get_sheet(sheet, spreadsheetId, range)

    if 'charts' in sheet_properties['sheets'][0]:
        for chart in sheet_properties['sheets'][0]['charts']:

            requests = {
                "deleteEmbeddedObject": {
                    "objectId": chart['chartId']
                }
            }

            body = {
                "requests": requests
            }

            sheet.batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()


def graph_process_data(sheet, spreadsheetId, range='A:F'):

    data_dict = rearrange_data_from_sheet(sheet, spreadsheetId, test_name)

    if data_dict:
        clear_sheet_data(sheet, spreadsheetId, range)
        clear_sheet_charts(sheet, spreadsheetId, range)
    else:
        raise Exception("Data sheet empty")

    for data in data_dict:
        machine_class = data[0][0].split('.')[0]

        value_range_body = {
            'values': data
        }

        response = sheet.values().append(spreadsheetId=spreadsheetId,
                                         range=range,
                                         valueInputOption='USER_ENTERED',
                                         body=value_range_body).execute()

        updated_range = response['updates']['updatedRange']

        # apply_named_range(sheet, spreadsheetId, machine_class, updated_range)

        graph_data(sheet, spreadsheetId, updated_range)


def rearrange_data_from_sheet(sheet, spreadsheetId, range='A:F'):
    """
    For linpack
    """
    values = read_sheet(sheet, spreadsheetId, range=test_name)

    data_dict = {}

    for row in values[1:]:
        key = row[0].split('.')[0]
        if cloud_type == 'AWS':
            if key in data_dict:
                data_dict[row[0].split('.')[0]] += [row]
            else:
                data_dict[row[0].split('.')[0]] = [row]

    return data_dict.values()


if __name__ == '__main__':
    test_name = 'linpack'
    cloud_type = 'AWS'
    creds = authenticate_creds()
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    spreadsheetId = '1aUwUL99-FHfH0NdbxfGW886sqSEXVU2yVBOXAJf2RXc'

    graph_process_data(sheet, spreadsheetId, test_name)

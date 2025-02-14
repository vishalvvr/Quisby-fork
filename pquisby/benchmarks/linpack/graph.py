import time
from itertools import groupby

from pquisby.sheet.sheetapi import sheet
from pquisby.sheet.sheet_util import (
    clear_sheet_charts,
    clear_sheet_data,
    append_to_sheet,
    read_sheet,
    get_sheet,
)


# TODO: remove mention of range with test_name


# def rearrange_linpack_data(spreadsheetId, range="A:F"):
#     """
#     Retreived data is sorted into groups by machine name

#     :sheet: sheet API function
#     :spreadsheetId
#     :range: range to graph up the data, it will be mostly sheet name
#     """
#     sorted_result = []

#     values = read_sheet(spreadsheetId, range=range)

#     # Clear empty rows
#     values = list(filter(None, values))
#     header_row = [values[0]]
#     # Pop Header row to sort by system size
#     values = [row for row in values if row[0] != "System"]

#     for _, items in groupby(values, key=lambda x: x[0].split(".")[0]):
#         sorted_data = sorted(
#             list(items), key=lambda x: int(x[0].split(".")[1].split("x")[0])
#         )

#         sorted_result.append(header_row + sorted_data)

#     return sorted_result

def create_series_range_linpack(column_count, sheetId, start_index, end_index):
    """"""
    series = []

    for index in range(column_count):

        series.append(
            {
                "series": {
                    "sourceRange": {
                        "sources": [
                            {
                                "sheetId": sheetId,
                                "startRowIndex": start_index,
                                "endRowIndex": end_index,
                                "startColumnIndex": index + 1,
                                "endColumnIndex": index + 2,
                            }
                        ]
                    }
                },
                "type": "COLUMN",
            }
        )

    return series

def graph_linpack_data(spreadsheetId, test_name):
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
    :test_name: test_name
    """
    GFLOPS_PLOT_RANGE = "C"
    PRICE_PER_PERF_RANGE = "E"
    GRAPH_COL_INDEX = 5
    GRAPH_ROW_INDEX = 0
    start_index, end_index = None, None

    data = read_sheet(spreadsheetId, test_name)
    header_row = data[0]

    for index, row in enumerate(data):
        if row[0] == "System" and start_index is None:
            start_index = index
            continue

        if start_index is not None:
            if index + 1 == len(data):
                end_index = index + 1
            elif data[index + 1][0] == "System":
                end_index = index + 1

        if end_index:
            graph_data = data[start_index:end_index]
            column_count = len(graph_data[0])

            sheetId = get_sheet(spreadsheetId, test_name)["sheets"][0]["properties"][
                "sheetId"
            ]

            # GFlops & GFlops scaling graph
            requests = {
                "addChart": {
                    "chart": {
                        "spec": {
                            "title": "%s and %s"
                            % (header_row[2], header_row[3]),
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
                                        % (header_row[2], header_row[3]),
                                    },
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
                                                        "startRowIndex": start_index,
                                                        "endRowIndex": end_index,
                                                        "startColumnIndex": 2,
                                                        "endColumnIndex": 3,
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
                                                        "startRowIndex": start_index,
                                                        "endRowIndex": end_index,
                                                        "startColumnIndex": 3,
                                                        "endColumnIndex": 4,
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
                                    "columnIndex": column_count + 1,
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
                            "title": "%s " % (header_row[5]),
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
                                        "title": "%s " % (header_row[5]),
                                    },
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
                                                        "startRowIndex": start_index,
                                                        "endRowIndex": end_index,
                                                        "startColumnIndex": 5,
                                                        "endColumnIndex": 6,
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
                                    "columnIndex": column_count + 7,
                                }
                            }
                        },
                    }
                }
            }

            body = {"requests": requests}

            sheet.batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()

            GRAPH_ROW_INDEX += 20
            start_index, end_index = None, None

            time.sleep(1)

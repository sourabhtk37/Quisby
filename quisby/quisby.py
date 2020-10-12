import sys

import config.config as config
from sheet.sheetapi import sheet
from sheet.sheet_util import create_sheet, append_to_sheet, create_spreadsheet
from stream.stream import extract_stream_data, create_summary_stream_data
from stream.graph import graph_stream_data
from uperf.uperf import extract_uperf_data, create_summary_uperf_data
from uperf.graph import graph_uperf_data
from specjbb.specjbb import extract_specjbb_data, create_summary_specjbb_data
from specjbb.graph import graph_specjbb_data
from pig.extract import extract_pig_data
from pig.graph import graph_pig_data
from pig.summary import create_summary_pig_data
from linpack.extract import extract_linpack_summary_data
from linpack.summary import create_summary_linpack_data
from linpack.graph import graph_linpack_data


def process_results(results):
    """"""
    if results:

        results = globals()[f"create_summary_{test_name}_data"](results)

        create_sheet(config.spreadsheetId, test_name)
        append_to_sheet(config.spreadsheetId, results, test_name)

        # Graphing up data
        globals()[f"graph_{test_name}_data"](config.spreadsheetId, test_name)

    return []


# TODO: simplify functions once data location is exact


def data_handler(path):
    """"""
    global test_name

    spreadsheet_name = f"{config.cloud_type} {config.OS_TYPE}-{config.OS_RELEASE}"

    results = []

    with open(path) as file:
        test_result_path = file.readlines()

        for data in test_result_path:
            if "tests" in data:
                results = process_results(results)
                test_name = data.split("_")[-1].strip()

                if not config.spreadsheetId:
                    config.spreadsheetId = create_spreadsheet(
                        spreadsheet_name, test_name
                    )
            else:
                # Create test path
                if data:

                    # Strip new line and "'"
                    data = data.strip("\n").strip("'")
                    system_name = data.split("/")[1].strip()
                    result_name = data.split("/")[-1].strip("\n")

                    if test_name == "stream":
                        test_path = (
                            f"rhel_{config.OS_RELEASE}/{data}"
                            f"/{result_name}/streams_results/"
                            f"{result_name}/results_streams.csv"
                        )

                        results += extract_stream_data(test_path, system_name)

                    # TODO: support url fetching
                    elif test_name == "uperf":
                        system_name = data.split("_")[3].split(":")[0].strip()
                        test_path = (
                            f"rhel_{config.OS_RELEASE}/uperf_results_{config.OS_RELEASE}/"
                            f"{data}result.csv"
                        )

                        results += extract_uperf_data(test_path, system_name)

                    elif test_name == "linpack":
                        test_path = f"rhel_{config.OS_RELEASE}/" f"{data}/summary.csv"

                        ret_val = extract_linpack_summary_data(test_path, system_name)
                        if ret_val:
                            results += ret_val

                    # TODO: support url fetching
                    elif test_name == "specjbb":
                        system_name = data.split("_")[2].strip("/")

                        test_path = (
                            f"rhel_{config.OS_RELEASE}/specjbb_results_{config.OS_RELEASE}/"
                            f"{data}SPECjbb.001.results"
                        )

                        results.append(extract_specjbb_data(test_path, system_name))

                    elif test_name == "pig":

                        test_path = (
                            f"rhel_{config.OS_RELEASE}/"
                            f"{data}/iteration_1.{system_name}"
                        )

                        results.append(extract_pig_data(test_path, system_name))

        results = process_results(results)

        print(f"https://docs.google.com/spreadsheets/d/{config.spreadsheetId}")


def main():

    try:
        arg = sys.argv[1]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} <test results location file>")

    config.OS_RELEASE = arg.split("_")[-1]
    data_handler(arg)
    # TODO: Multi-spreadsheet support
    # config.spreadsheetId = sys.argv[2]
    # spreadsheets = return dictionary_spreadsheets
    # comparison_wrapper(spreadsheets)


if __name__ == "__main__":
    main()

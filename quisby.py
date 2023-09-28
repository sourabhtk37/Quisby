import json
import os.path
import fileinput
import sys
import time
import logging

from quisby.benchmarks.coremark.coremark import extract_coremark_data, create_summary_coremark_data
from quisby.benchmarks.coremark.graph import graph_coremark_data

from quisby.benchmarks.coremark_pro.coremark_pro import extract_coremark_pro_data, create_summary_coremark_pro_data
from quisby.benchmarks.coremark_pro.graph import graph_coremark_pro_data

from quisby.benchmarks.passmark.passmark import extract_passmark_data, create_summary_passmark_data
from quisby.benchmarks.passmark.graph import graph_passmark_data

from quisby.benchmarks.pyperf.pyperf import extract_pyperf_data, create_summary_pyperf_data
from quisby.benchmarks.pyperf.graph import graph_pyperf_data

from quisby.benchmarks.streams.streams import extract_streams_data, create_summary_streams_data
from quisby.benchmarks.streams.graph import graph_streams_data
from quisby.benchmarks.streams.comparison import compare_streams_results

from quisby.benchmarks.uperf.uperf import extract_uperf_data, create_summary_uperf_data
from quisby.benchmarks.uperf.graph import graph_uperf_data
from quisby.benchmarks.uperf.comparison import compare_uperf_results

from quisby.benchmarks.specjbb.specjbb import extract_specjbb_data, create_summary_specjbb_data
from quisby.benchmarks.specjbb.comparison import compare_specjbb_results
from quisby.benchmarks.specjbb.graph import graph_specjbb_data

from quisby.benchmarks.pig.extract import extract_pig_data
from quisby.benchmarks.pig.graph import graph_pig_data
from quisby.benchmarks.pig.summary import create_summary_pig_data
from quisby.benchmarks.pig.comparison import compare_pig_results

from quisby.benchmarks.linpack.extract import extract_linpack_data
from quisby.benchmarks.linpack.summary import create_summary_linpack_data
from quisby.benchmarks.linpack.graph import graph_linpack_data
from quisby.benchmarks.linpack.comparison import compare_linpack_results

from quisby.benchmarks.hammerdb.extract import extract_hammerdb_data
from quisby.benchmarks.hammerdb.summary import create_summary_hammerdb_data
from quisby.benchmarks.hammerdb.graph import graph_hammerdb_data
from quisby.benchmarks.hammerdb.comparison import compare_hammerdb_results

from quisby.benchmarks.fio.fio import process_fio_run_result, extract_fio_run_data
from quisby.benchmarks.fio.summary import create_summary_fio_run_data
from quisby.benchmarks.fio.graph import graph_fio_run_data
from quisby.benchmarks.fio.comparison import compare_fio_run_results

from quisby.benchmarks.reboot.reboot import extract_boot_data
from quisby.benchmarks.reboot.summary import create_summary_boot_data
from quisby.benchmarks.reboot.graph import graph_boot_data

from quisby.benchmarks.aim.extract import extract_aim_data
from quisby.benchmarks.aim.summary import create_summary_aim_data
from quisby.benchmarks.aim.graph import graph_aim_data

from quisby.benchmarks.autohpl.extract import extract_autohpl_data
from quisby.benchmarks.autohpl.summary import create_summary_autohpl_data
from quisby.benchmarks.autohpl.graph import graph_autohpl_data

from quisby.benchmarks.speccpu.extract import extract_speccpu_data
from quisby.benchmarks.speccpu.summary import create_summary_speccpu_data
from quisby.benchmarks.speccpu.graph import graph_speccpu_data
from quisby.benchmarks.speccpu.comparison import compare_speccpu_results

from quisby.benchmarks.etcd.etcd import extract_etcd_data, create_summary_etcd_data, graph_etcd_data, \
    compare_etcd_results

from quisby.util import read_config, write_config
from quisby.sheet.sheet_util import clear_sheet_charts, clear_sheet_data, get_sheet, create_sheet, append_to_sheet, \
    create_spreadsheet
from quisby.logging.logging_configure import configure_logging


def check_test_is_hammerdb(test_name):
    if test_name in ["hammerdb_pg", "hammerdb_maria", "hammerdb_mssql"]:
        return True
    else:
        return False


def process_results(results, test_name, cloud_type, os_type, os_release, spreadsheet_name, spreadsheetid):

    # Summarise data
    try:
        if check_test_is_hammerdb(test_name):
            results = create_summary_hammerdb_data(results)
        else:
            logging.info("Summarising " + test_name + " data...")
            results = globals()[f"create_summary_{test_name}_data"](results, os_release)
    except Exception as exc:
        logging.error("Failed to summarise data")
        return spreadsheetid

    # Append data
    try:
        create_sheet(spreadsheetid, test_name)
        logging.info("Deleting existing charts and data from the sheet...")
        clear_sheet_charts(spreadsheetid, test_name)
        clear_sheet_data(spreadsheetid, test_name)
        logging.info("Appending new " + test_name + " data to sheet...")
        append_to_sheet(spreadsheetid, results, test_name)
    except Exception as exc:
        logging.error("Failed to append data to sheet")
        return spreadsheetid

    # Graph up data
    try:
        logging.info("Graphing " + test_name + " data...")
        if check_test_is_hammerdb(test_name):
            graph_hammerdb_data(spreadsheetid, test_name)
        else:
            globals()[f"graph_{test_name}_data"](spreadsheetid, test_name)
    except Exception as exc:
        logging.error("Failed to graph data")
        return spreadsheetid

    return spreadsheetid


def register_details_json(spreadsheet_name, spreadsheet_id):
    logging.info("Collecting spreadsheet information...")
    home_dir = os.getenv("HOME")
    filename = home_dir + "/.config/quisby/charts.json"
    if not os.path.exists(filename):
        data = {"chartlist": {spreadsheet_name: spreadsheet_id}}
        with open(filename, "w") as f:
            json.dump(data, f)
    else:
        with open(filename, "r") as f:
            data = json.load(f)
        data["chartlist"][spreadsheet_name] = spreadsheet_id
        with open(filename, "w") as f:
            json.dump(data, f)
    logging.info({spreadsheet_name: spreadsheet_id})


# TODO: simplify functions once data location is exact
def data_handler():
    """"""
    global test_name
    global source
    global count
    results = []

    logging.info("Loading configurations...")
    cloud_type = read_config('cloud', 'cloud_type')
    os_type = read_config('test', 'OS_TYPE')
    os_release = read_config('test', 'OS_RELEASE')
    spreadsheet_name = read_config('spreadsheet', 'spreadsheet_name')
    spreadsheetid = read_config('spreadsheet', 'spreadsheet_id')
    test_path = read_config('test', 'test_path')
    results_path = read_config('test', 'results_location')

    if not spreadsheetid:
        logging.info("Creating a new spreadsheet... ")
        spreadsheet_name = f"{cloud_type}-{os_type}-{os_release}-{spreadsheet_name}"
        spreadsheetid = create_spreadsheet(spreadsheet_name, "summary")
        write_config("spreadsheet", "spreadsheet_id", spreadsheetid)
        write_config("spreadsheet", "spreadsheet_name", spreadsheet_name)
        logging.info("Spreadsheet name : " + spreadsheet_name)
        logging.info("Spreadsheet ID : " + spreadsheetid)
    else:
        logging.warning("Collecting spreadsheet information from config...")
        logging.info("Spreadsheet name : " + spreadsheet_name)
        logging.info("Spreadsheet ID : " + spreadsheetid)
        logging.info("Spreadsheet : " + f"https://docs.google.com/spreadsheets/d/{spreadsheetid}")
        logging.warning("!!! Quit Application to prevent overwriting of existing data !!!")
        time.sleep(10)
        logging.info("No action provided. Overwriting the existing sheet.")

    # Strip empty lines from location file
    for line in fileinput.FileInput(results_path, inplace=1):
        if line.rstrip():
            #print(line, end="")
            pass


    with open(results_path) as file:
        logging.info("Reading data files path provided in file : " + results_path)
        test_result_path = file.readlines()
        for data in test_result_path:
            if "test " in data:
                if results:
                    spreadsheetid = process_results(results, test_name, cloud_type, os_type, os_release,
                                                    spreadsheet_name, spreadsheetid)
                results = []
                test_name = data.replace("test ", "").strip()
                print("********************** Extracting and preprocessing " + str(test_name) + " data "
                                                                                                "**********************")
                source = "results"
            elif "new_series" in data:
                continue
            else:
                try:
                    if test_name == "fio_run":
                        data = data.strip("\n").strip("'").strip()
                        path, system_name = (data.split(",")[0] + "," + data.split(",")[1]), data.split(",")[-1]
                        path = path.replace("/" + os.path.basename(path), "")
                    else:
                        data = data.strip("\n").strip("'")
                        path, system_name = data.split(",")
                    path = test_path + "/" + path.strip()
                    logging.debug(path)
                    if test_name == "streams":
                        ret_val = extract_streams_data(path, system_name, os_release)
                        if ret_val:
                            results += ret_val
                    elif test_name == "uperf":
                        ret_val = extract_uperf_data(path, system_name)
                        if ret_val:
                            results += ret_val
                    elif test_name == "linpack":
                        ret_val = extract_linpack_data(path, system_name)
                        if ret_val:
                            results += ret_val
                    elif test_name == "specjbb":
                        ret_value = extract_specjbb_data(path, system_name, os_release)
                        if ret_value is not None:
                            results.append(ret_value)
                    elif test_name == "pig":
                        ret_val = extract_pig_data(path, system_name, os_release)
                        if ret_val:
                            results += ret_val
                    elif check_test_is_hammerdb(test_name):
                        ret_val = extract_hammerdb_data(path, system_name, test_name, os_release)
                        if ret_val:
                            results += ret_val
                    elif test_name == "fio_run":
                        ret_val = None
                        if source == "results":
                            ret_val = extract_fio_run_data(path, system_name, os_release)
                        elif source == "pbench":
                            ret_val = process_fio_run_result(path, system_name)
                        if ret_val:
                            results += ret_val
                        pass
                    elif test_name == "boot":
                        ret_val = extract_boot_data(path, system_name)
                        if ret_val:
                            results += ret_val
                    elif test_name == "aim":
                        ret_val = extract_aim_data(path, system_name)
                        if ret_val:
                            results += ret_val
                    elif test_name == "autohpl":
                        ret_val = extract_autohpl_data(path, system_name)
                        if ret_val:
                            results += ret_val
                    elif test_name == "speccpu":
                        ret_val = extract_speccpu_data(path, system_name, os_release)
                        if ret_val:
                            results += ret_val
                    elif test_name == "etcd":
                        ret_val = extract_etcd_data(path, system_name)
                        if ret_val:
                            results += ret_val
                    elif test_name == "coremark":
                        ret_val = extract_coremark_data(path, system_name, os_release)
                        if ret_val:
                            results += ret_val
                    elif test_name == "coremark_pro":
                        ret_val = extract_coremark_pro_data(path, system_name, os_release)
                        if ret_val:
                            results += ret_val
                    elif test_name == "passmark":
                        ret_val = extract_passmark_data(path, system_name, os_release)
                        if ret_val:
                            results += ret_val
                    elif test_name == "pyperf":
                        ret_val = extract_pyperf_data(path, system_name, os_release)
                        if ret_val:
                            results += ret_val
                    else:
                        logging.info("Mentioned benchmark not yet supported ! ")

                except Exception as exc:
                    logging.error(str(exc))

        if results is not []:
            try:
                spreadsheetid = process_results(results, test_name, cloud_type, os_type, os_release, spreadsheet_name,
                                                spreadsheetid)
            except Exception as exc:
                logging.error(str(exc))
                pass
            logging.info(f"https://docs.google.com/spreadsheets/d/{spreadsheetid}")
            register_details_json(spreadsheet_name, spreadsheetid)


def compare_results(spreadsheets):
    sheet_list = []
    spreadsheet_name = []
    comparison_list = []
    test_name = []

    logging.info("Comparing the data provided..")
    logging.info("Collecting list of benchmarks...")
    for spreadsheet in spreadsheets:
        sheet_names = []
        sheets = get_sheet(spreadsheet, test_name=test_name)
        spreadsheet_name.append(get_sheet(spreadsheet, test_name=[])["properties"]["title"].strip())
        for sheet in sheets.get("sheets"):
            sheet_names.append(sheet["properties"]["title"].strip())
        sheet_list.append(sheet_names)

    if test_name:
        comparison_list = [test_name]
    else:
        # Find sheets that are present in all spreadsheets i.e intersection
        logging.info("Extracting common benchmarks for comparison...")
        comparison_list = set(sheet_list[0])
        for sheets in sheet_list[1:]:
            comparison_list.intersection_update(sheets)
        comparison_list = list(comparison_list)

    logging.info("Creating new spreadsheet..")

    spreadsheet_name = read_config('spreadsheet', 'comp_name')
    spreadsheetid = read_config('spreadsheet', 'comp_id')

    if not spreadsheetid:
        logging.info("Creating a new spreadsheet... ")
        spreadsheet_name = " and ".join(spreadsheet_name)
        spreadsheetid = create_spreadsheet(spreadsheet_name, comparison_list[0])
        write_config("spreadsheet", "comp_id", spreadsheetid)
        write_config("spreadsheet", "comp_name", spreadsheet_name)
        logging.info("Spreadsheet name : " + spreadsheet_name)
        logging.info("Spreadsheet ID : " + spreadsheetid)
    else:
        logging.warning("Collecting spreadsheet information from config...")
        logging.info("Comp spreadsheet name : " + spreadsheet_name)
        logging.info("Comp spreadsheet ID : " + spreadsheetid)
        logging.info("Spreadsheet : " + f"https://docs.google.com/spreadsheets/d/{spreadsheetid}")
        logging.warning("!!! Quit Application to prevent overwriting of existing data !!!")
        time.sleep(10)
        logging.info("No action provided. Overwriting the existing sheet.")

    for index, test_name in enumerate(comparison_list):
        try:
            logging.info("Comparing " + test_name + " value...")
            write_config("test", "test_name", test_name)
            if check_test_is_hammerdb(test_name):
                compare_hammerdb_results(spreadsheets, spreadsheetid, test_name)
            else:
                globals()[f"compare_{test_name}_results"](spreadsheets, spreadsheetid, test_name)
            if index + 1 != len(comparison_list):
                logging.info(
                    "# Sleeping 10 sec to workaround the Google Sheet per minute API limit"
                )
                time.sleep(10)
        except Exception as exc:
            logging.error("Benchmark " + test_name + " comparison failed")

    logging.info(f"https://docs.google.com/spreadsheets/d/{spreadsheetid}")
    register_details_json(spreadsheet_name, spreadsheetid)


def reduce_data():
    data_handler()


def compare_data(s_list):
    compare_results(s_list)


# Set up logging
configure_logging()

if __name__ == "__main__":
    print(
        "**************************************** STARTING QUISBY APPLICATION **************************************** ")
    if len(sys.argv) > 1:
        if sys.argv[1] == "process":
            reduce_data()
        elif sys.argv[1] == "compare":
            try:
                s_list = sys.argv[2].split(",")
                compare_data(s_list)
            except Exception as exc:
                logging.error("Please provide a valid list of spreadsheets to compare")
        else:
            logging.warning("Incorrect options provided.Proceeding with default action...")
            reduce_data()
    else:
        logging.warning("No options provided.Proceeding with default action...")
        reduce_data()

from itertools import groupby

import quisby.config as config
from quisby.util import mk_int, process_instance


def stream_sort_data_by_system_family(results):
    """"""
    stream_data = []
    sorted_result = []

    for index in range(0, len(results), 7):
        stream_data.append(results[index : index + 7])

    stream_data.sort(
        key=lambda x: str(process_instance(x[2][0], "family", "version", "feature"))
    )

    for _, items in groupby(
        stream_data,
        key=lambda x: process_instance(x[2][0], "family", "version", "feature"),
    ):

        sorted_result.append(
            sorted(list(items), key=lambda x: mk_int(process_instance(x[2][0], "size")))
        )
        
    return sorted_result


def calc_max_throughput(data):
    """"""
    num_of_socket = data[1][0].split(" ")[0]
    system_name = data[2][0]
    max_copy = max(data[3][1:])
    max_scale = max(data[4][1:])
    max_add = max(data[5][1:])
    max_triad = max(data[6][1:])

    return [
        system_name + " Sockets:" + num_of_socket,
        max_copy,
        max_scale,
        max_add,
        max_triad,
    ]


def create_summary_streams_data(stream_data):
    """
    Create summary data for Max throughput and Scaling
    """
    results = []
    stream_data = stream_sort_data_by_system_family(stream_data)

    # Group by system family
    for items in stream_data:
        max_calc_result = []
        for item in items:
            results += item
            max_calc_result.append(calc_max_throughput(item))
        results.append([""])
        results.append(
            [
                "Max Througput",
                f"Copy-{config.OS_RELEASE}",
                f"Scale-{config.OS_RELEASE}",
                f"Add-{config.OS_RELEASE}",
                f"Triad-{config.OS_RELEASE}",
            ]
        )

        results += max_calc_result

    return results


def extract_streams_data(path, system_name):
    """
    Extracts streams data and appends empty list for each seperate stream runs

    :path: stream summary results file from stream_wrapper_benchmark runs
    :system_name: machine name (eg: m5.2xlarge, Standard_D64s_v3)
    """

    with open(path) as file:
        streams_results = file.readlines()

    # # Streams data is sorted by socket number
    # data_index = 0
    # for index, data in enumerate(streams_results):
    #     if "buffer size" in data:
    #         data_index = index
    #     streams_results[index] = data.strip("\n").split(":")

    # # Slice and sort only necessary data by socket number, column 2
    # streams_results = sorted(streams_results[data_index + 1 :], key=lambda x: x[2])

    # # A list of list is created which has format
    # # [[''], ['<Socket number>'], [system_name], [<COPY data>],
    # # [<SCALE data>], [<ADD data>], [<TRIAD data>]]

    # socket_number = ""
    # proccessed_data = []
    # if not streams_results:
    #     return None
    # for row in streams_results:
    #     if socket_number != row[2]:
    #         socket_number = row[2]
    #         proccessed_data += (
    #             [""],
    #             [f"{socket_number} Socket"],
    #             [system_name],
    #             ["Copy"],
    #             ["Scale"],
    #             ["Add"],
    #             ["Triad"],
    #         )

    #     # Appending copy, scale, add and triad data

    #     pos = len(proccessed_data)
    #     data_pos = len(row)

    #     # Append stream array size
    #     proccessed_data[pos - 5].append(row[0] + "-" + config.OS_RELEASE)

    #     # append each function data
    #     for index in range(1, 5):
    #         proccessed_data[pos - index].append(row[data_pos - index])

    # return proccessed_data

    flag = False
    system_metadata = []
    streams_data = []

    for row in streams_results:
        if "Optimization level: O3" in row:
            flag = True
        if flag:
            if "%" in row:
                system_metadata.append([row.strip("%").split()])
            elif "Socket" in row:
                streams_data.append([""])
                streams_data.append([f"{row.strip()}"])
                streams_data.append(
                    [system_name, 
                    f"33m-{config.OS_RELEASE}", 
                    f"66m-{config.OS_RELEASE}", 
                    f"132m-{config.OS_RELEASE}", 
                    f"264m-{config.OS_RELEASE}"])
            else:
                if "\n" != row:
                    streams_data.append(row.strip("\n").split(":"))
    
    return streams_data


if __name__ == "__main__":
    extract_streams_data(
        "results_streams.csv",
        "i3en.xlarge",
    )

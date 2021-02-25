from itertools import groupby

import quisby.config as config
from quisby.util import mk_int


def fio_sort_data(results):
    sorted_result = []
    # group data
    results = [list(g) for k, g in groupby(results, key=lambda x: x != [""]) if k]

    # sort results together by operation and operation size
    results.sort(key=lambda x: (x[0][1], x[0][2], x[0][0].split(".")[0]))

    for _, items in groupby(
        results, key=lambda x: (x[0][0].split(".")[0], x[0][1], x[0][2])
    ):
        sorted_result += sorted(
            list(items), key=lambda x: mk_int(x[0][0].split(".")[1].split("x")[0])
        )

    return sorted_result


def create_summary_fio_data(results):
    summary_results = []
    run_metric = {"1024KiB": "iops", "4KiB": "lat"}

    results = fio_sort_data(results)

    for key, items in groupby(
        results, key=lambda x: (x[0][0].split(".")[0], x[0][1], x[0][2])
    ):
        run_data = {}

        items = list(items)
        columns = [
            i[0][0] + f"-{run_metric[i[0][2].split('-')[0]]}-{config.OS_RELEASE}"
            for i in items
        ]

        for index, item in enumerate(items):
            # Add individual data tables
            summary_results.append([""])
            summary_results += item

            # Create and filter summary on 1 disk & 1 job
            item = list(
                filter(
                    lambda x: (
                        int(x[0].split("-")[0].split("_")[0]) == 1
                        and int(x[0].split("-")[1].split("_")[0]) == 1
                    ),
                    item[2:],
                )
            )
            # Pick only the first three results, 
            # since xlarge systems have duplicated data
            
            for ele in item:

                if ele[0] in run_data:
                    for _ in range(index - len(run_data[ele[0]])):
                        run_data[ele[0]].append("")
                    run_data[ele[0]].append(ele[1])
                else:
                    run_data[ele[0]] = [""] * index
                    run_data[ele[0]].append(ele[1])

        summary_results.append([""])
        summary_results.append([*key[:2], f"{key[2]}"])
        summary_results.append(["Iteration Name", *columns])
        for key, value in run_data.items():
            summary_results.append([key, *value])

    return summary_results

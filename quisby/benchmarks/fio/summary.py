from itertools import groupby

import quisby.config as config
from quisby.util import mk_int, process_instance


def fio_sort_data(results):
    sorted_result = []
    # group data
    results = [list(g) for k, g in groupby(
        results, key=lambda x: x != [""]) if k]

    # sort results together by operation and operation size
    results.sort(key=lambda x: (x[0][1], x[0][2], str(
        process_instance(x[0][0], "family", "version", "feature"))))

    for _, items in groupby(
        results, key=lambda x: (process_instance(
            x[0][0], "family", "version", "feature"), x[0][1], x[0][2])
    ):
        sorted_result += sorted(
            list(items), key=lambda x: mk_int(process_instance(x[0][0], "size"))
        )

    return sorted_result


def create_summary_fio_data(results):
    summary_results = []
    run_metric = {"1024KiB": "iops", "4KiB": "lat", "2300KiB": "iops"}

    results = fio_sort_data(results)

    for header, items in groupby(
        results, key=lambda x: (process_instance(
            x[0][0], "family", "version", "feature"), x[0][1], x[0][2])
    ):
        run_data = {}

        items = list(items)
        columns = [
            i[0][0] +
            f"-{run_metric[i[0][2].split('-')[0]]}-{config.OS_RELEASE}"
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

            for ele in item:

                if ele[0] in run_data:
                    for _ in range(index - len(run_data[ele[0]])):
                        run_data[ele[0]].append("")
                    run_data[ele[0]].append(ele[1])
                else:
                    run_data[ele[0]] = [""] * index
                    run_data[ele[0]].append(ele[1])

        instance_type = ''.join(item for item in header[0] if item)

        summary_results.append([""])
        summary_results.append([instance_type, header[1], header[2]])
        summary_results.append(["iteration_name", *columns])
        for key, value in run_data.items():
            summary_results.append([key, *value])

    return summary_results

from itertools import groupby

from quisby.util import mk_int, process_instance


def fio_run_sort_data(results):
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


def create_summary_fio_run_data(results,OS_RELEASE):
    """ Create summary of the extracted raw data
        Parameters
        ----------
        results : list
            Extracted raw data from results location"""
    summary_results = []
    try:
        results = fio_run_sort_data(results)
    except Exception as exc:
        print(str(exc))
    for header, items in groupby(results, key=lambda x: [x[0][0],x[0][1],x[0][2]]):
        try:
            items = list(items)
            summary_results.append([""])
            summary_results.append([header[0], header[1], header[2]])
            summary_results.append(["iteration_name", items[0][1][1]])
            for index, item in enumerate(items):
                # Add individual data tables
                summary_results.append(item[2])
        except Exception as exc:
            pass
    return summary_results

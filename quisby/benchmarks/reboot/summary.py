from itertools import groupby


def create_summary_boot_data(results):
    sorted_results = []

    results = list(filter(None, results))
    header_row = [results[0]]
    results = [row for row in results if row[0] != "System name"]

    for _, items in groupby(sorted(results), key=lambda x: x[0].split(".")[0]):

        sorted_data = sorted(
            list(items), key=lambda x: int(x[0].split(".")[1].split("x")[0])
        )

        sorted_results += header_row + sorted_data

    return sorted_results
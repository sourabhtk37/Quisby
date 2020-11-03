from itertools import groupby


def pig_sort_data_by_system_family(results):
    sorted_result = []

    results.sort(key=lambda x: x[1][0].split(".")[0])

    for _, items in groupby(results, key=lambda x: x[1][0].split(".")[0]):
        sorted_result.append(
            sorted(list(items), key=lambda x: int(x[1][0].split(".")[1].split("x")[0]))
        )

    return sorted_result


def create_summary_pig_data(pig_data):
    results = []

    pig_data = pig_sort_data_by_system_family(pig_data)

    for items in pig_data:
        for item in items:
            results += item

    return results

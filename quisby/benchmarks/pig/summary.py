from itertools import groupby

from quisby.util import mk_int


def pig_sort_data_by_system_family(results):
    sorted_result = []
    
    results = [list(g) for k, g in groupby(results, key=lambda x: x != [""]) if k]
    
    results.sort(key=lambda x: x[0][0].split(".")[0])

    for _, items in groupby(results, key=lambda x: x[0][0].split(".")[0]):
        sorted_result.append(
            sorted(                                 
                list(items), key=lambda x: mk_int(x[0][0].split(".")[1].split("x")[0])
            )
        )

    return sorted_result


def create_summary_pig_data(pig_data):
    results = []

    pig_data = pig_sort_data_by_system_family(pig_data)
    
    for items in pig_data:
        for item in items:
            results.append([""])
            results += item

    return results

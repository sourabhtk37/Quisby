from itertools import groupby

# TODO: Add support for azure systems
def hammerdb_sort_data_by_system_family(results):
    sorted_result = []

    results.sort(key=lambda x: x[0][1].split(".")[0])

    # if cloud_type == 'AWS':
    for _, items in groupby(results, key=lambda x: x[0][1].split(".")[0]):

        sorted_result.append(
            sorted(list(items), key=lambda x: int(x[0][1].split(".")[1].split("x")[0]))
        )

    return sorted_result


def create_summary_hammerdb_data(hammerdb_data):
    results = []

    hammerdb_data = hammerdb_sort_data_by_system_family(hammerdb_data)

    for data in hammerdb_data:
        run_data = {}

        results.append([""])
        results.append([data[0][0][0]])

        for row in data:

            results[-1] += [row[0][1]]

            for ele in row[1:]:
                if ele[0] in run_data:
                    run_data[ele[0]].append(ele[1])
                else:
                    run_data[ele[0]] = [ele[1]]

        for key, item in run_data.items():
            results.append([key, *item])

    return results

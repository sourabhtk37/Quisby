from itertools import groupby


def create_summary_linpack_data(results):

    sorted_results = []

    results = list(filter(None, results))
    header_row = [results[0]]
    results = [row for row in results if row[0] != "System"]

    for _, items in groupby(sorted(results), key=lambda x: x[0].split(".")[0]):
        sorted_data = sorted(
            list(items), key=lambda x: int(x[0].split(".")[1].split("x")[0])
        )
        
        cpu_scale, base_gflops = None, None
        for index, row in enumerate(sorted_data):
            if not cpu_scale and not base_gflops:
                cpu_scale = int(row[1])
                base_gflops = float(row[2])
            else:
                gflops_scaling = float(row[2]) / (int(row[1]) - cpu_scale) / base_gflops
                sorted_data[index][3] = format(gflops_scaling, ".4f")

        sorted_results += header_row + sorted_data
    print(sorted_results)

    return sorted_results

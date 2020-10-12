from itertools import groupby

import config.config as config
from pricing.cloud_pricing import get_aws_pricing


def specjbb_sort_data_by_system_family(results):

    sorted_result = []

    results.sort(key=lambda x: x[1][0].split('.')[0])

    for _, items in groupby(results, key=lambda x: x[1][0].split('.')[0]):
        sorted_result.append(
            sorted(list(items), key=lambda x: int(x[1][0].split('.')[1].split('x')[0])))

    return sorted_result


def calc_peak_throughput_peak_efficiency(data):
    cost_per_hour = get_aws_pricing(data[1][0], config.region)
    peak_throughput = max(data[3:], key=lambda x: int(x[1]))[1]
    peak_efficiency = float(peak_throughput) / float(cost_per_hour)

    return peak_throughput, cost_per_hour, peak_efficiency


def create_summary_specjbb_data(specjbb_data):
    """
    """
    results = []

    specjbb_data = specjbb_sort_data_by_system_family(specjbb_data)

    for items in specjbb_data:
        peak_throughput, cost_per_hour, peak_efficiency = [], [], []

        for item in items:
            results += item
            pt, cph, pe = calc_peak_throughput_peak_efficiency(item)
            peak_throughput.append([item[1][0], pt])
            cost_per_hour.append([item[1][0], cph])
            peak_efficiency.append([item[1][0], pe])

        results.append([""])
        results.append(["Peak", f"Thrput-{config.OS_RELEASE}"])
        results += peak_throughput
        results.append([""])
        results.append(["Cost/Hr"])
        results += cost_per_hour
        results.append([""])
        results.append(["Peak/$eff", f"Price/perf-{config.OS_RELEASE}"])
        results += peak_efficiency

    return results


def extract_specjbb_data(path, system_name):
    """
    """
    results = [[""], [system_name]]

    # File read
    with open(path) as file:
        specjbb_results = file.readlines()

    # Find position of SPEC Scores
    start_index, end_index = 0, 0
    for index, row in enumerate(specjbb_results):

        if 'SPEC scores' in row:
            start_index = index + 1

        if start_index:
            if not row.strip('\n'):
                end_index = index - 2
                break

    # Extract data and convert to a list
    for row in specjbb_results[start_index:end_index]:
        row = row.strip(' ').strip('*').strip(' ').strip('\n').split(' ')

        if row[-1] == 'Thrput':
            row[-1] = row[-1]+f"-{config.OS_RELEASE}"

        results.append([row[0], row[-1]])

    return results

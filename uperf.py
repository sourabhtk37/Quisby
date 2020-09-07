import pprint
import csv

from config import *

pp = pprint.PrettyPrinter()

# TODO: Include all ports results
def extract_uperf_data(path, system_name):
    results = []

    with open(path) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        index_trans, index_latency = [], []
        iteration_name = []
        header_row = []

        for index, row in enumerate(csv_reader):
            bandwidth, trans, latency = [], [], []
            instance_count = row['iteration_name'].split('-')[2:][0]

            # pop failed runs
            if 'fail' in row['iteration_name']:
                continue

            # remove empty values
            row = {k: v for k, v in row.items() if v is not '' and k is not None}

            for k, v in row.items():
                if 'Gb_sec' in k:
                    bandwidth = v
                elif 'trans_sec' in k:
                    trans = v
                elif 'usec' in k:
                    latency = v

            # Process results and create list(results) for appending to sheet
            if bandwidth:
                if iteration_name != row['iteration_name'].split('-')[:2]:

                    iteration_name = row['iteration_name'].split('-')[:2]
                    results.append([""])
                    results.append([system_name])
                    results.append(["-".join(iteration_name)])
                    # for _ in len(bandwidth):
                    header_row = [i.split(':')[0]
                                  for i in list(row.keys())[2:]]
                    results.append([*(['instance count']+ ['Gb_sec'])])

                results.append([instance_count, bandwidth])
            else:
                header_row = [i.split(':')[0]
                              for i in list(row.keys())[2:]]
                if iteration_name != row['iteration_name'].split('-')[:2]:

                    iteration_name = row['iteration_name'].split('-')[:2]
                    index_trans.append([""])
                    index_trans.append([system_name])
                    index_trans.append(["-".join(iteration_name)])
                    index_trans.append(
                        [*(['instance count'] + ['trans_sec'])])

                    index_latency.append([""])
                    index_latency.append([system_name])
                    index_latency.append(["-".join(iteration_name)])
                    index_latency.append(
                        [*(['instance count'] + ['usec'])])

                index_trans.append([instance_count, trans])
                index_latency.append([instance_count, latency])

        results += index_trans
        results += index_latency

        return results


if __name__ == "__main__":
    print(extract_uperf_data('uperf_results/tcp-udp-multiple-results.csv', 'i3en.xlarge'))

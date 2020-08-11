import pprint

from config import *

pp = pprint.PrettyPrinter()

# TODO: Bad and hacky code, need more results data to generalise
# WIP
def extract_uperf_data(path, system_name):
    """
    """
    results = []
    average_trans = []
    average_latency = []

    with open(path) as file:
        uperf_result = file.readlines()

        for index, data in enumerate(uperf_result):

            if 'Test' in data:
                test_name = data

            elif 'GB/sec' in data:
                nic_count_bw = len(uperf_result[index+1].split(':')[2:])

            elif 'trans/sec' in data:
                nic_count_lat = len(uperf_result[index+1].split(':')[2:])

            elif 'packet_size' in data:
                system_name = data.split(':')[2].split(' ')[0]
                packet_size = []

            else:
                row_data = data.strip('\n').split(':')
                packet_size.append(row_data.pop(0))
                uperf_instance_count = row_data.pop(0)

                # average of NICs
                if len(row_data) > 4:
                    if len(packet_size) == 1:
                        average_trans.append([""])
                        average_trans.append([system_name])
                        average_trans.append([test_name])
                        average_trans.append(
                            ['Trans/sec', '%s Nics' % (nic_count_lat)])
                        average_trans.append(
                            ['Packet Size', 'Instances', 'Trans/sec'])

                        average_latency.append([""])
                        average_latency.append([system_name])
                        average_latency.append([test_name])
                        average_latency.append(
                            ['Latency (us)', '%s Nics' % (nic_count_lat)])
                        average_latency.append(
                            ['Packet Size', 'Instances', 'latency (us)'])
                    average_trans.append(
                        [packet_size[-1] + ' Bytes', uperf_instance_count+' instance', sum(map(float, row_data[:4]))/4])
                    average_latency.append(
                        [packet_size[-1] + ' Bytes', uperf_instance_count+' instance', sum(map(float, row_data[4:]))/4])

                else:
                    average_bw = sum(map(float, row_data))/4
                    if len(packet_size) == 1:
                        results.append([""])
                        results.append([system_name])
                        results.append([test_name])
                        results.append(
                            ['Bandwidth GB/sec', '%s Nics' % (nic_count_bw)])
                        results.append(['Packet Size', 'Instances', 'GB/sec'])
                    results.append(
                        [packet_size[-1] + ' Bytes', uperf_instance_count+' instance', average_bw])

        results += average_trans
        results += average_latency

    return results


if __name__ == "__main__":
    print(extract_uperf_data('uperf_result', 'i3en.xlarge'))

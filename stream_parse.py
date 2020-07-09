
def extract_stream_data(path, results=['<System name>']):
    """
    Extracts streams data and takes average of multiple iterations 
    """
    streams_data = {}
    with open(path) as file:
        streams_results = file.readlines()

        for index, data in enumerate(streams_results):
            if 'Array size' in data:

                iter_result = []
                for result in streams_results[index+21:index+25]:
                    iter_result.append(result.split()[0:2])

                array_size = data.split()[3]
                if array_size in streams_data.keys():
                    for index, value in enumerate(streams_data[array_size]):

                        streams_data[array_size][index][1] = round(
                            (float(value[1])+float(iter_result[0][1]))/2, 1)
                else:
                    streams_data.update({data.split()[3]: iter_result})
    results = [results+list(streams_data.keys())]
    results += ['Copy'], ['Scale'], ['Add'], ['Triad']

    for stream_type in streams_data.values():
        for value in range(len(streams_data)):
            results[value+1].append(stream_type[value][1])

    return results


if __name__ == '__main__':
    path = 'results_streams_tuned_tuned_virtual-guest_sys_file_none/streams_results/streams_O3_tuned_virtual-guest_sys_file_none.out'
    print(extract_stream_data(path, ['perf64']))

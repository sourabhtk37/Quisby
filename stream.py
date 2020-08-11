from operator import itemgetter

from util import *
from config import *


def extract_stream_data(path, system_name='System'):
    """
    Extracts streams data and appends empty list for each seperate stream runs

    :path: stream summary results file from stream_wrapper_benchmark runs
    :system_name: machine name (eg: m5.2xlarge, Standard_D64s_v3)
    """

    with open(path) as file:
        streams_results = file.readlines()

    # Streams data is sorted by socket number
    data_index = 0
    for index, data in enumerate(streams_results):
        if 'buffer size' in data:
            data_index = index
        streams_results[index] = data.strip('\n').split(':')

    streams_results = sorted(
        streams_results[data_index+1:], key=itemgetter(2))

    # A list of list is created which has format
    # [[''], ['<Socket number>'], [system_name], [<COPY data>],
    # [<SCALE data>], [<ADD data>], [<TRIAD data>]]

    socket_number = ''
    proccessed_data = []
    for x in streams_results:
        if socket_number != x[2]:
            socket_number = x[2]
            proccessed_data += [''], ['%s Socket' % x[2]], [system_name], [
                'Copy'], ['Scale'], ['Add'], ['Triad']

        # Appending copy, scale, add and triad data
        pos = len(proccessed_data)
        pos_line = len(x)
        proccessed_data[pos - 5].append(x[0])
        for i in range(1, 5):
            proccessed_data[pos-i].append(x[pos_line-i])

    print(proccessed_data)


if __name__ == '__main__':
    extract_stream_data(stream_path, 'i3en.xlarge')
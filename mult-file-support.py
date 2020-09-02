from stream import extract_stream_data
from config import *
from util import *
from data_reduction import main


def data_handler(path):
    """
    """
    with open(path) as file:
        test_result_path = file.readlines()

        for data in test_result_path:
            if 'tests' in data:
                if 'results' in data:
                    test_name = data.split('_')[-1]
                    if test_name.strip() == "streams":
                        test_name = 'stream'
            else:
                system_name = data.split('/')[1]
                test_path = 'rhel8.3_result' + \
                    data.strip('.').strip('\n')+'/results_streams.csv'

                main(test_name, test_path, system_name)


if __name__ == '__main__':
    data_handler("test_locations")

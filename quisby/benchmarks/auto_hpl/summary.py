from quisby.benchmarks.linpack.summary import create_summary_linpack_data


def create_summary_auto_hpl_data(results,OS_RELEASE):
    return create_summary_linpack_data(results,OS_RELEASE)
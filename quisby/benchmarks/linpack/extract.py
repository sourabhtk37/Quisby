import csv
import glob
import re
import os.path

from quisby.pricing import cloud_pricing
import quisby.config as config

def extract_linpack_summary_data(path):
    """
    Make shift function to handle linpack summary data
    till a resolution is reached
    """

    results = []
    no_of_cores = None
    gflops= None
    
    system_name = path.split("/")[4]
    summary_file = path + "/summary.csv"
    
    if not os.path.isfile(summary_file):
        return None    
    
    with open(summary_file) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=":")
        last_row = list(csv_reader)[-2]
        gflops = last_row["MB/sec"]
        threads = last_row["threads"]

    for file_path in glob.glob(path + f"/linpack*_threads_{threads}_*"):
        with open(file_path) as txt_file:
            data = txt_file.readlines()
            for row in data:
                if re.findall(r"Number of cores: (\d+)", row):
                    no_of_cores = re.findall(r"Number of cores: (\d+)", row)[0]
                    break

    if gflops:
        get_cloud_pricing = getattr(
            cloud_pricing, "get_%s_pricing" % config.cloud_type.lower()
        )
        price_per_hour = get_cloud_pricing(system_name, config.region)
        
        results.append(
            [
                "System",
                "Cores",
                f"GFLOPS-{config.OS_RELEASE}",
                f"GFLOP Scaling-{config.OS_RELEASE}",
                "Cost/hr",
                f"Price/Perf-{config.OS_RELEASE}",
            ]
        )
        results.append(
            [
                system_name,
                no_of_cores,
                gflops,
                1,
                price_per_hour,
                float(gflops) / float(price_per_hour),
            ]
        )
        
        return results
import csv
import glob
import re
import tarfile

from quisby.pricing import cloud_pricing
import quisby.config as config

def extract_linpack_summary_data(path):
    """
    Make shift function to handle linpack summary data
    till a resolution is reached
    """

    results = []
    system_name = path.split("/")[3]

    result_tar = glob.glob(path + "results_linpack*.tar")[0]
    tar = tarfile.open(result_tar)
    tar_files = tar.getnames()
    summary_file=tar.getmember(tar_files[0]+"/summary.csv")

    with tar.extractfile(summary_file) as csv_file:
        csv_reader = csv_file.readlines()
        last_row = str(list(csv_reader)[-1]).split(':')
        gflops = last_row[-2]
        threads = last_row[2]
    
    search_str = r".*linpack_.*threads_"+re.escape(threads)+ r"_.*"
    for file_path in tar_files:            
        match_path = re.findall(search_str, file_path, re.IGNORECASE)
        if match_path:
            with tar.extractfile((tar.getmember(match_path[0]))) as txt_file:
                data = txt_file.readlines()
                for row in data:
                    row = str(row)
                    if re.findall(r"Number of cores: (\d+)", row):
                        no_of_cores = re.findall(r"Number of cores: (\d+)", row)[0]
                        break
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

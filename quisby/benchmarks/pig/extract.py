import re

import quisby.config as config


def extract_pig_data(path):
    results = []
    result_data = []
    cpu_count = 0

    system_name = path.split("/")[4]
    path = path + f"/iteration_1.{system_name}"
    with open(path) as file:

        for line in file:
            if "PID" in line:
                cpu_data, thread_data = re.findall(r"(\w+\:\s\w+)", line)[1:3]
                efficiency = float(cpu_data.split()[1]) / float(thread_data.split()[1])
                result_data.append([thread_data.split()[1], efficiency])
            if not cpu_count:
                match = re.findall(r"(\w+\s\w+\s)(\d+)(\scpus)", line)
                if match:
                    cpu_count = match[0][1]

        results.append([""])
        results.append([system_name, f"CpuCount: {cpu_count}"])
        results.append(["Threads", f"{config.OS_RELEASE}"])
        results += result_data

    return results

import re
import tarfile


def extract_boot_data(path, system_name):
    results = []

    # system_name = path.split("_")[2]
    try:
        with open(path + "/cloud_timings") as file:
            data = file.readlines()

            instance_start_time = re.findall(r"instance start_time:\s+(\d+)", data[0])[0]
            terminate_time = re.findall(r"terminate time:\s+(\d+)", data[1])[0]

    except FileNotFoundError:
        return []

    tar = tarfile.open(path + "reboot_boot_info/reboot_boot_info_1.tgz")
    for member in tar.getmembers():
        if "reboot_timings" in str(member):
            file = tar.extractfile(member)
            data = file.readlines()

            reboot_time = re.findall(r"reboot time:\s+(\d+)", str(data))[0]

    if instance_start_time and terminate_time and reboot_time:
        results.append(["System name", "Start Time", "Terminate Time", "Reboot Time"])
        results.append([system_name, instance_start_time, terminate_time, reboot_time])

    return results

import logging
import tarfile
import os
import re
import argparse
from itertools import groupby
import glob

logging.basicConfig(level=logging.DEBUG)


def untar_files(path):
    locations = []

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".tar") and file.startswith("results"):
                file_path = os.path.join(root, file)

                logging.info(f"untar {file_path}")
                tar = tarfile.open(file_path)
                extracted_file_name = tar.getnames()[0]
                tar.extractall(root)
                tar.close()
                logging.info(f"untar {file_path} done")

                try:
                    result_name = re.search("results(_pbench)?_(.+?)_", file).group(2)
                    system_name = root.split("/")[-1].strip("_0")

                except AttributeError:
                    print("Unknown results file")
                    logging.warning(f"Issue with result: {file_path}, ignoring")
                    continue

                locations.append(
                    [result_name, root + "/" + extracted_file_name, system_name]
                )

    return locations


def create_location_file(locations, result_location):
    locations = sorted(locations, key=lambda x: x[0])

    with open(result_location, "a") as result_file:
        logging.info("Creating location file")

        for location, paths in groupby(locations, key=lambda x: x[0]):

            if location == "streams":
                result_file.write(f"test: results_{location.rstrip('s')}\n")
                for path in paths:
                    result_name = path[1].split("/")[-1].strip("\n")
                    logging.info(f"processing {path}")
                    path = (
                        f"{path[1]}/streams_results/"
                        f"{result_name}"
                        f"/results_streams.csv,{path[2]}\n"
                    )

                    result_file.write(path)

            elif location == "specjbb":
                result_file.write(f"test: results_{location}\n")
                for path in paths:
                    logging.info(f"specjbb: Find oldest file {path}")
                    older_file = max(
                        os.listdir(path[1]),
                        key=lambda f: os.path.getctime(f"{path[1]}/{f}"),
                    )
                    updated_path = (
                        f"{path[1]}/"
                        f"{older_file}/SPECjbbSingleJVM/SPECjbb.001.results,{path[2]}\n"
                    )
                    result_file.write(updated_path)

            elif location == "hammerdb":
                continue

            elif location == "uperf":
                result_file.write(f"test: results_{location}\n")

                for path in paths:
                    updated_path = f"{path[1]}/" f"result.csv,{path[2]}\n"
                    result_file.write(updated_path)

            elif location == "auto":
                result_file.write(f"test: results_{location}hpl\n")
                for path in paths:
                    files = glob.glob(f"{path[1]}/*.log")
                    try:
                        logging.info(f"auto: Finding older of the two file {files}")
                        older_file = max(
                            files,
                            key=lambda f: os.path.getctime(f"{f}"),
                        )
                    except ValueError as e:
                        logging.warning(f"Data not present for {path[1]}. Skipping")
                        continue

                    if older_file:
                        updated_path = f"{older_file},{path[2]}\n"
                        result_file.write(updated_path)
            elif "speccpu" in location:
                result_file.write(f"test:results_speccpu\n")
                for path in paths:
                    result_file.write(f"{path[1]},{path[2]}\n")

            else:
                result_file.write(f"test: results_{location}\n")
                for path in paths:
                    result_file.write(f"{path[1]},{path[2]}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Zathras specific tool to untar and create location file for quisby"
    )

    parser.add_argument(
        "--path",
        action="store",
        required=True,
        help="Provide location to zath systems dir",
    )
    parser.add_argument(
        "-o", "--output", action="store", required=True, help="Output file"
    )
    args = parser.parse_args()

    locations = untar_files(args.path)
    create_location_file(locations, args.output)


if __name__ == "__main__":
    main()

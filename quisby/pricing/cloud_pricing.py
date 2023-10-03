# Using this package which is a HTTP library
import logging
import sys
import time
import json
import requests
import boto3
from quisby.util import process_instance, read_config
import os

homedir = os.getenv("HOME")
json_path = homedir + "/.config/quisby/azure_prices.json"


def fetch_from_url():
    url = "https://azure.microsoft.com/api/v3/pricing/virtual-machines/calculator"
    try:
        response = requests.get(url)
    except Exception as exc:
        logging.error(str(exc))
    if response.status_code == 200:
        return response.json()
    else:
        logging.error("Error: {}".format(response.text))
        return None


def get_azure_pricing(instance_name, region):
    prefix = instance_name.split("_")
    series = ""
    version = ""
    tier = ""
    try:
        series = prefix[1].lower()
        tier = prefix[0].lower()
        version = prefix[2].lower()
    except Exception as exc:
        logging.debug(str(exc))
        logging.info("Version not present")
    vm = "linux-" + series + version + "-" + tier

    if os.path.exists(homedir + json_path):
        # fetch price information from json
        try:
            with open(homedir + json_path) as f:
                data = json.load(f)
        except Exception as exc:
            logging.error("Error extracting data from file. File corrupted. Redirecting to url fetching.")
            data = fetch_from_url()
    else:
        # fetch price information from url
        data = fetch_from_url()
    if data is None:
        return data
    price = data.json()["offers"][vm]['prices']['perhour'][region]["value"]
    logging.info("VM SKU: {}".format(instance_name))
    logging.info("Hourly price: {} USD".format(price))
    return price


def get_gcp_prices(instance_name, region):
    url = "https://cloudpricingcalculator.appspot.com/static/data/pricelist.json"

    response = requests.get(url, stream=True)
    decoded_response = response.content.decode("UTF-8")
    google_ext_prices = json.loads(decoded_response)
    price_data = {}
    if "gcp_price_list" not in google_ext_prices:
        sys.stderr.write('Google Cloud pricing data missing "gcp_price_list" node\n')
        return None
    prefix = ""
    gcp_price_list = google_ext_prices["gcp_price_list"]
    machine_fam = instance_name.split("-")[0].upper()
    if machine_fam in ("N2", "N2D", "T2D", "T2A", "C2", "C2D", "M1", "M2"):
        prefix = "CP-COMPUTEENGINE-" + machine_fam + "-PREDEFINED-VM-CORE".strip()
    elif machine_fam in ("N1", "E2"):
        prefix = 'CP-COMPUTEENGINE-VMIMAGE-' + instance_name.upper().strip()
    else:
        logging.error("This machine price is not available")
        return

    for name, prices in gcp_price_list.items():
        if prefix == name:
            for key, price in prices.items():
                if region == key:
                    return gcp_price_list[name][region]
            return


def get_aws_instance_info(instance_name, region):
    """
    AWS pricing is retreived using the aws boto3 client pricing API.

    Following args are used for filtering results
    :instance_name: eg: "m5.2xlarge"
    :region: eg: "US East (N. Virginia)"

    returns: integer pricing in USD
    """
    region = read_config("cloud", "region")
    pricing = boto3.client("pricing", region_name=region)

    OPERATING_SYSTEM = "AmazonEC2"
    response = pricing.get_products(
        ServiceCode=OPERATING_SYSTEM,
        Filters=[
            {
                'Type': 'TERM_MATCH',
                'Field': 'ServiceCode',
                'Value': OPERATING_SYSTEM
            },
        ],
        FormatVersion='aws_v1',
        MaxResults=1
    )

    return response['PriceList']


def get_aws_pricing(instance_name, region):
    price_list = get_aws_instance_info(instance_name, region)

    # Filter pricing details
    if price_list:
        price_item = json.loads(price_list[0])

        terms = price_item["terms"]

        price_dimension = terms["OnDemand"][iter(terms["OnDemand"]).__next__()][
            "priceDimensions"
        ]
        price = price_dimension[iter(price_dimension).__next__()]["pricePerUnit"]["USD"]

        return price
    else:
        return None


def get_aws_cpucount(instance_name, region):
    cpu_count = 1
    price_list = get_aws_instance_info(instance_name, region)

    if price_list:
        price_item = json.loads(price_list[0])

        cpu_count = price_item["product"]["attributes"]["vcpu"]

    return cpu_count


def get_cloud_pricing(instance_name, region, cloud_type):
    if cloud_type == "aws":
        return get_aws_pricing(instance_name, region)

    elif cloud_type == "azure":
        return get_azure_pricing(instance_name, region)

    elif cloud_type == "gcp":
        return get_gcp_prices(instance_name, region)

    elif cloud_type == "local":
        return 1


def get_cloud_cpu_count(instance_name, region, cloud_type):
    if cloud_type == "aws":
        return get_aws_cpucount(instance_name, region)

    elif cloud_type == "azure":
        return int(process_instance(instance_name, "size"))

    elif cloud_type == "gcp":
        return int(process_instance(instance_name, "size"))

    elif cloud_type == "local":
        return 1


if __name__ == "__main__":
    # region = "us-east"
    # print(get_azure_pricing("Standard_D32s_v3",region))
    # print(get_aws_cpucount("i3en.24xlarge",region))
    # print(get_gcp_prices("n2-standard-16",region)
    pass

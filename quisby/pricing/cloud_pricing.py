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


# ToDo: Timestamp work
def get_azure_pricing(system_name, region="US Gov"):
    """
    The following call is made before to retreive pricing information:

    az rest -m get --header "Accept=application/json" -u
    "https://management.azure.com/subscriptions/<subscription-ID>/providers/
    Microsoft.Commerce/RateCard?api-version=2015-06-01-preview&%24filter=
    OfferDurableId eq 'MS-AZR-0003p' and Currency eq 'USD' and
    Locale eq 'en-US' and RegionInfo eq 'US'" > azure_prices.json

    Not considering Windows systems. Filtering is not efficient,
    should be improved further.

    :system_name: azure system name to filter the results eg: "Standard_F32s_v2", "Standard_D64s_v3"
    :region: region to filter results eg: "US East 2"

    returnrs: integer pricing in USD
    """

    # current_time = datetime.datetime.now()

    # file_mod_time = datetime.datetime.fromtimestamp(
    #     getmtime("azure_prices.json"))

    # time_diff = current_time - file_mod_time

    # if time_diff.days > 5:
    #     print("Azure pricing info older than 30 days. Updating")
    #     process = subprocess.run(['az', 'rest', '-m', 'get', '--header', '"Accept=application/json"', '-u', '"https://management.azure.com/subscriptions/106f53c3-524c-477b-a44b-703ebe9cfd49/providers/Microsoft.Commerce/RateCard?api-version=2015-06-01-preview&%24filter=OfferDurableId eq "MS-AZR-0003p" and Currency eq "USD" and Locale eq "en-US" and RegionInfo eq "US""'],
    #                                stdout=subprocess.PIPE,
    #                                universal_newlines=True)

    #     print(process)

    with open("azure_prices.json", "r") as read_file:
        data = json.load(read_file)

        name, version = system_name.split("_")[1:]
        system_name = str(name + " " + version)

        for resource in data["Meters"]:
            if (
                len(resource["MeterName"]) <= 14
                and "Windows" not in resource["MeterSubCategory"]
            ):
                if (
                    system_name in str(resource["MeterName"])
                    and resource["MeterRegion"] == "US East 2"
                ):
                    return resource["MeterRates"]["0"]


def get_gcp_prices(instance_name, region):
    url = "https://cloudpricingcalculator.appspot.com/static/data/pricelist.json"

    # Get previous price list
    try:
        with open(homedir+"/.config/quisby/gcp_prices.json") as file_in:
            price_data = json.loads(file_in.read())
    except Exception as exc:
        logging.ERROR("Doesn't exist")

    response = requests.get(url, stream=True)
    decoded_response = response.content.decode("UTF-8")
    google_ext_prices = json.loads(decoded_response)

    if "gcp_price_list" not in google_ext_prices:
        sys.stderr.write('Google Cloud pricing data missing "gcp_price_list" node\n')
        return None

    gcp_price_list = google_ext_prices["gcp_price_list"]
    prefix = instance_name.split("-")
    instance_name = prefix[0].upper()
    for name, prices in gcp_price_list.items():
        if not instance_name in name:
            continue
        for key, price in prices.items():
            if region in key:
                try:
                    price_data["compute"][region][name] = price
                except Exception as exc:
                    price_data = {}
                    price_data["compute"] = {}
                    price_data["compute"][region] = {}
                    price_data["compute"][region][name] = price

    # Update last-modified timestamp.
    try:
        price_data["updated"] = int(time.time())
    except Exception as exc:
        price_data["updated"] = int(time.time())

    with open("/Users/soumyasinha/.config/quisby/gcp_prices.json", "w") as file_out:
        json_str = json.dumps(price_data)
        file_out.write(json_str)


def get_aws_instance_info(instance_name, region):
    """
    AWS pricing is retreived using the aws boto3 client pricing API.

    Following args are used for filtering results
    :instance_name: eg: "m5.2xlarge"
    :region: eg: "US East (N. Virginia)"

    returns: integer pricing in USD
    """
    region = read_config("cloud","region")
    pricing = boto3.client("pricing",region_name=region)

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
        return get_gcp_prices(instance_name, region)

    elif cloud_type == "local":
        return 1



if __name__ == "__main__":
    region = "US East 2"
    print(get_azure_pricing("Standard_D32s_v3", region))
    # print(get_aws_cpucount("i3en.24xlarge", "US East (N. Virginia)"))

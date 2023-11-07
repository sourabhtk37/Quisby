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
def list_aws_regions(region):
    try:
        ec2 = boto3.client('ec2',region)
        regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']
                   if region['OptInStatus'] != 'not-opted-in']
        return regions
    except Exception as exc:
        print("Unable to fetch aws regions")
        return None

def list_operating_systems(region):
    try:
        client = boto3.client('pricing', region_name=region)

        response = client.get_products(ServiceCode='AmazonEC2')

        operating_systems = set()

        if 'PriceList' in response:
            for price_list in response['PriceList']:
                product = json.loads(price_list)
                if 'attributes' in product['product']:
                    attributes = product['product']['attributes']
                    if 'operatingSystem' in attributes:
                        os = attributes['operatingSystem']
                        operating_systems.add(os)
        return operating_systems
    except Exception as exc:
        print("Unable to fetch OS list")
        return None

def get_aws_instance_info(instance_name, region):
    """
    AWS pricing is retreived using the aws boto3 client pricing API.

    Following args are used for filtering results
    :instance_name: eg: "m5.2xlarge"
    :region: eg: "US East (N. Virginia)"

    returns: integer pricing in USD
    """
    pricing = boto3.client("pricing", region_name=region)

    OPERATING_SYSTEM = "AmazonEC2"
    response = pricing.get_products(
        ServiceCode=OPERATING_SYSTEM,
        Filters=[
            {
                'Type': 'TERM_MATCH',
                'Field': 'ServiceCode',
                'Value': OPERATING_SYSTEM,

            },
        ],
        FormatVersion='aws_v1',
        MaxResults=1
    )

    return response['PriceList']


def get_aws_pricing(instance_type, region, os_type):
    product = "AmazonEC2"
    client = boto3.client('pricing', region_name=region)
    filters = [
        {"Type": "TERM_MATCH", "Field": "regionCode", "Value": region},
        {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
        {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": os_type},
    ]

    response = client.get_products(ServiceCode=product, Filters=filters)

    if "PriceList" in response:
        try:
            price_list = json.loads(response["PriceList"][0])

            # Extract pricing information as needed
            terms = price_list["terms"]["OnDemand"]
            for _, term_info in terms.items():
                for _, price_dimension in term_info["priceDimensions"].items():
                    price_per_hour = price_dimension["pricePerUnit"]["USD"]
                    print(
                        f"Price per Hour: for " + instance_type + " for os " + os_type + " in region " + region + " is " + price_per_hour + " USD")
                    return price_per_hour
        except Exception as exc:
            print("Unable to fetch prices of " + instance_type + " for os_type " + os_type + " in region " + region)
            return None


def get_instance_vcpu_count(instance_type, region):
    ec2 = boto3.client('ec2', region_name=region)

    instance_info = ec2.describe_instance_types(InstanceTypes=[instance_type])

    if 'InstanceTypes' in instance_info:
        instance = instance_info['InstanceTypes'][0]
        vcpu_count = instance['VCpuInfo']['DefaultVCpus']
        return vcpu_count
    else:
        return None


def get_cloud_pricing(instance_name, region, cloud_type,os_type):
    if cloud_type == "aws":
        return get_aws_pricing(instance_name, region,os_type)

    elif cloud_type == "azure":
        return get_azure_pricing(instance_name, region)

    elif cloud_type == "gcp":
        return get_gcp_prices(instance_name, region)

    elif cloud_type == "local":
        return 1


def get_cloud_cpu_count(instance_name, region, cloud_type):
    if cloud_type == "aws":
        return get_instance_vcpu_count(instance_name, region)

    elif cloud_type == "azure":
        return int(process_instance(instance_name, "size"))

    elif cloud_type == "gcp":
        return int(process_instance(instance_name, "size"))

    elif cloud_type == "local":
        return 1


if __name__ == "__main__":
    # print(get_azure_pricing("Standard_D32s_v3",region))
    # print(get_gcp_prices("n2-standard-16",region)
    region = "us-east-1"  # Replace with your desired AWS region
    instance_type = ["m6i.xlarge", "m6i.24xlarge"]  # Replace with your desired EC2 instance type
    os_type = ["rhel", "Linux", "Ubuntu Pro"]
    list_aws_regions(region)
    list_operating_systems(region)
    for instance in instance_type:
        for os in os_type:
            get_instance_vcpu_count(instance, region)
            get_aws_pricing(instance,region, os)

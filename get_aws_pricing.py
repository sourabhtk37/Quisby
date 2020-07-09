import boto3

import pprint
import json

pricing = boto3.client('pricing')

OPERATING_SYSTEM = 'Linux'
OPERATION = 'RunInstances'
TENANCY = 'Shared'
PRE_INSTALLED_SW = 'NA'
CAPACITY_STATUS = 'UnusedCapacityReservation'


def get_ondemand_hourly_price(instance_name, region):
    """
    """
    response = pricing.get_products(
        ServiceCode='AmazonEC2',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'operatingSystem',
                'Value': OPERATING_SYSTEM},
            {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_name},
            {'Type': 'TERM_MATCH', 'Field': 'operation', 'Value': OPERATION},
            {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': TENANCY},
            {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw',
                'Value': PRE_INSTALLED_SW},
            {'Type': 'TERM_MATCH', 'Field': 'Location', 'Value': region},
            {'Type': 'TERM_MATCH', 'Field': 'capacitystatus',
                'Value': CAPACITY_STATUS}
        ],
        MaxResults=100
    )

    price_list = response['PriceList']

    if price_list:
        price_item = json.loads(price_list[0])

        terms = price_item["terms"]

        price_dimension = terms["OnDemand"][iter(
            terms["OnDemand"]).__next__()]["priceDimensions"]
        price = price_dimension[iter(
            price_dimension).__next__()]['pricePerUnit']["USD"]

        return price
    else:
        return None


if __name__ == '__main__':
    print(get_ondemand_hourly_price('i3en.24xlarge', 'US East (N. Virginia)'))

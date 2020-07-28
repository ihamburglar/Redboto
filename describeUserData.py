#!/usr/bin/env python3
# Original Author @elitest
# This script is part of Redboto
# https://github.com/elitest/Redboto/

# This script uses boto3 and texttable to print
# userData from EC2 instances from each region

# Wishlist:
# allow you to specify a specific host
import boto3, base64
from texttable import Texttable


#connection stricly to get regions
client = boto3.client(service_name='ec2', region_name='us-east-1')
regions = client.describe_regions()['Regions']

#Iterate through the regions
for region in regions:
    print('[*] Checking region ' + region['RegionName'] + '\n')
    ec2 = boto3.resource(service_name='ec2', region_name=region['RegionName'])

    # Start building the table
    table = Texttable()
    table.set_cols_align(["c", "l"])
    table.set_cols_valign(["m", "m"])
    table.set_cols_width([20,80])
    table.header(["InstanceID", "UserData"])

    # this is used to not print the table if there is no data in this region
    isData = False

    # iterate through instances to look for userData
    for instance in ec2.instances.all():
        response = instance.describe_attribute(Attribute='userData')
        instanceid = ec2.Instance(instance.id).id

        # Probably a better way to do this PRs accepted!
        try:
            if response['UserData']['Value']:
                # add to the table if we have data
                table.add_row([instanceid , base64.b64decode(response['UserData']['Value'])])
                # this turns on printing of the table for this region at the end of this for loop
                isData = True
        except KeyError:
            break

    # If we have data in this region print the table
    if isData:
        print(table.draw() + '\n')

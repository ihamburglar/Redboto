#!/usr/bin/env python3
# Original Author @elitest
# This script is part of RedDolphin
# https://github.com/elitest/RedDolphin/

# This script uses boto3 and texttable to print
# information about EC2 instances

# Wishlist:
# Add information such as networking, tags, etc.
# Add control over which attributes are printed
# Add the ability to specify profile and region

import boto3, json
from texttable import Texttable

#connection stricly to get regions
client = boto3.client(service_name='ec2', region_name='us-east-1')
regions = client.describe_regions()['Regions']

#Iterate through the regions
#for region in regions:

for region in regions:

    print("checking region: "+region['RegionName'] + "\n")
    ec2 = boto3.client(service_name='ec2', region_name=region['RegionName'])
    response = ec2.describe_instances()

    table = Texttable()
    table.set_cols_align(["c", "c", "c", "c", "c"])
    table.set_cols_valign(["m", "m", "m", "m", "m"])
    #tablearray = []
    #tablearray.append(["Instance ID", "Name", "State", "VolumeId"])
    if response['Reservations']:
    	table.header(["Instance ID", "Name", "State", "VolumeId", "DeviceName"])
        for r in response['Reservations']:
	        for i in r['Instances']:
		      	instanceid = i['InstanceId']
		        ec2 = boto3.resource('ec2', region['RegionName'])
		        Instance = ec2.Instance(i['InstanceId'])
		        if Instance.tags:
		            for tag in Instance.tags:
		            	if tag['Key'] == 'Name':
		            		name = tag['Value']
		        #There may be another condition here
		    	else:
		            name = " "
		        state = i['State']['Name']
		        vs = ''
		        dn = ''
		        for d in i['BlockDeviceMappings']:
		            vs = vs + d['Ebs']['VolumeId'] + '\n'
		            dn = dn + d['DeviceName'] + '\n'
		        table.add_row([instanceid , name , state , vs, dn])
        print(table.draw() + "\n")
    else:
    	print('  No instances found in this region\n')

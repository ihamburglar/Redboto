#!/usr/bin/env python3
# Original Author @elitest
# This script is part of Redboto
# https://github.com/elitest/Redboto/

# This script uses boto3 and to take screenshots from EC2 hosts

# Wishlist:
# allow you to specify a specific host
# specify specific host
# python2 support?
import boto3, base64, os


#connection stricly to get regions
client = boto3.client(service_name='ec2', region_name='us-east-1')
regions = client.describe_regions()['Regions']

#Iterate through the regions
for region in regions:
    print('[*] Checking region ' + region['RegionName'] + '\n')
    ec2 = boto3.client('ec2', region_name=region['RegionName'])
    r = ec2.describe_instances()
    # iterate through instances to look for instances to screenshot
    for reservation in r["Reservations"]:
        for instance in reservation["Instances"]:
            id = instance['InstanceId']
            if instance['State']['Name'] == 'running':
                response = ec2.get_console_screenshot(InstanceId=id, WakeUp=True)
                filename = "screenshots/%s.jpeg" % id
                print('    [*] Found instance '+ id + ' writing ' + filename + '\n' )
                # This may be python3 specific
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(response['ImageData']))

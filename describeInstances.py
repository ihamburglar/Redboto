#!/usr/bin/env python3
# Original Author @elitest
# This script is part of Redboto
# https://github.com/elitest/Redboto

# This script uses boto3 and texttable to print
# information about EC2 instances

# Wishlist:
# Add information such as networking, tags, etc.
# Add control over which attributes are printed
# Add the ability to specify profile and region

import boto3, json, argparse, botocore.exceptions, sys
from texttable import Texttable

# Sets up the argument parser
argparser = argparse.ArgumentParser(description='Describe instances in EC2 in a table')
argparser.add_argument('--profile', default='default', help='The profile name in ~/.aws/credentials')
argparser.add_argument('--region', help='The region you want to describe instances of.  If not used, then all are listed.')
argparser.add_argument('--network', action='store_true', help='Includes IP addresses in the output.')
argparser.add_argument('--volume', action='store_true', help='Include volume information in the output.')
args = argparser.parse_args()

if args.profile:
    boto3.setup_default_session(profile_name=args.profile)

# This function pulls the information out of the EC2 instance and builds the table
def generate_table(region):
    ec2 = boto3.client(service_name='ec2', region_name=region)
    response = ec2.describe_instances()

    # Initialize the table unlimited width
    table = Texttable(max_width=0)

    # This is basically a builder for the width of the array used to build the table.
    tableWidth = 3
    if args.network:
         tableWidth +=2
    if args.volume:
         tableWidth +=2
    table.set_cols_align(tableWidth*["c"])
    table.set_cols_valign(tableWidth*["m"])

    # This is a builder for the names of the head of the table
    headerList = ["Instance ID", "Name", "State"]

    if args.volume:
        headerList += ["VolumeId","DeviceName"]
    if args.network:
        headerList += ["Private IPs", "Public IPs"]
    table.header(headerList)

    # If we get reservations iterate through them
    if response['Reservations']:
        for r in response['Reservations']:
            for i in r['Instances']:
                instanceid = i['InstanceId']
                # We actually need some information not accessible by the client
                ec2Resource = boto3.resource('ec2', region)
                Instance = ec2Resource.Instance(i['InstanceId'])

                # Name of the instance otherwise blank
                if Instance.tags:
                    for tag in Instance.tags:
                        if tag['Key'] == 'Name':
                            name = tag['Value']
                # There may be another condition here
                else:
                    name = ''

                # State of the instance
                state = i['State']['Name']

                # This is the builder for the add_row function
                rowList = [instanceid, name, state]

                if args.volume:
                    vs = ''
                    dn = ''
                    # Pull the device names
                    for d in i['BlockDeviceMappings']:
                        vs = vs + d['Ebs']['VolumeId'] + '\n'
                        dn = dn + d['DeviceName'] + '\n'
                    rowList += [vs,dn]

                if args.network:
                    # This pulls the IP addresses
                    # There are instances which may not have IPs
                    try:
                        public = i['PublicIpAddress']
                    except KeyError:
                        public = ''
                    try:
                        private = i['PrivateIpAddress']
                    except KeyError:
                        private = ''
                    rowList += [public,private]

                # This adds the row
                table.add_row(rowList)
        # This draws the table
        print(table.draw() + "\n")
    else:
        print('  No instances found in this region\n')

# This is if a region is specified in args
if args.region is not None:
    regions = {}
    regions = [{'RegionName': '%s' % args.region}]
else:
    #connection stricly to get regions
    client = boto3.client(service_name='ec2', region_name='us-east-1')
    regions = client.describe_regions()['Regions']

#Iterate through the regions
#for region in regions:
for region in regions:

    print("checking region: "+region['RegionName'] + "\n")
    try:
        generate_table(region['RegionName'])
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'UnauthorizedOperation':
            print('Are you sure you have the right permissions?  Check IAM.')
        elif error.response['Error']['Code'] == 'AuthFailure':
            print('Your keys may be invalid.  Perhaps they have been rotated?')
        #Something else happened here print the error code for inclusion above
        else:
            print(error.response['Error']['Code'])
    except botocore.exceptions.EndpointConnectionError as error:
        # Attempted to reach out to an invalid S3 endpoint
        print('Invalid region.  Check that you have specified a region that exists')
    except TypeError as error:
        # This is the case where no instances were found.
        # Too broad of an excaption perhaps?
        print('exception is' +error)
        pass
    except:
        # catch all exception
        print("I'm not sure what happened here.  Something else went wrong.",sys.exc_info())

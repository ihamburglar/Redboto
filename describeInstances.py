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

import boto3, json, argparse, botocore.exceptions, sys
from texttable import Texttable

argparser = argparse.ArgumentParser(description='Copies Registry Hives from a running system to an s3 bucket')
argparser.add_argument('--profile', default='default', help='The profile name in ~/.aws/credentials')
argparser.add_argument('--region', help='The region you want to describe instances of.  If not used, then all are listed.')
args = argparser.parse_args()

boto3.setup_default_session(profile_name=args.profile)

def generate_table(region):
    ec2 = boto3.client(service_name='ec2', region_name=region)
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
                ec2 = boto3.resource('ec2', region)
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

    print("checking region: "+args.region + "\n")

if args.region is not None:
    regions = {}
    regions = [{'RegionName': '%s' % args.region}]
else:
    #connection stricly to get regions
    client = boto3.client(service_name='ec2', region_name='us-east-1')
    regions = client.describe_regions()['Regions']
    print(regions)
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
    except TypeError:
        # This is the case where no instances were found.
        # Too broad of an excaption perhaps?
        pass
    except:
        # catch all exception
        print("I'm not sure what happened here.  Something else went wrong.",sys.exc_info())

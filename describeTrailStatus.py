#!/usr/bin/env python3
# Original Author @elitest
# This script is part of Redboto
# https://github.com/elitest/Redboto/

# This script uses boto3 and texttable to print
# userData from EC2 instances from each region

# TODO: Better API Key Support?
# API keys currently are loaded from a profile
# Better secret key handling?
# TODO: Better error handling
import boto3

#This loads the aws profile called 'default'
session = boto3.session.Session(profile_name='default', region_name='us-east-2b')
#We are just connecting to a random region in order to fetch a list of regions
ec2 = session.client('ec2', 'us-east-2')
#Get the regions
regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]

#Iterate through each region and check for the prescense of trails
#Probably need to do better error checking
#Pull requests accepted!
for region in regions:
    cloudtrail = boto3.client('cloudtrail', region)
    if not cloudtrail.describe_trails()['trailList']:
        print("[*] Region " + region + " doesn't appear to have Cloudtrails or you don't have permission")
    else:
        print("[-] Region " + region + " appears to have Cloudtrails")
        for trail in cloudtrail.describe_trails()['trailList']:
            print("    [+] Found a cloudtrail named: " + trail['Name'] + " in a bucket named: " + trail['S3BucketName'])
            if trail['LogFileValidationEnabled'] is True:
                print("        [+] Cloudtrail named: " + trail['Name'] + " has validation enabled.")
            else:
                print("        [+] Cloudtrail named: " + trail['Name'] + " does not have validation enabled.")

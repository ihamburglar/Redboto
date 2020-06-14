#!/usr/bin/env python3
# Original Author @elitest
# This script is part of RedDolphin
# https://github.com/elitest/RedDolphin/

# This script runs commands on a SSM host
#

# Wishlist:
# Currently just runs quick commands.  Need to check on status instead.
# Error checking?
# output to a file?
# interactive shell?

import boto3, argparse, botocore.exceptions, time

# Sets up the argument parser
argparser = argparse.ArgumentParser(description='Runs commands on SSM enabled hosts')
argparser.add_argument('--profile', default='default', help='The profile name in ~/.aws/credentials')
argparser.add_argument('--region', help='The region the instance is in.')
argparser.add_argument('instanceid', help='The InstanceID of the host with SSM installed and configured.')
argparser.add_argument('commandfile', help='The file with commands to be run.')
args = argparser.parse_args()

if args.profile:
    boto3.setup_default_session(profile_name=args.profile)

region = args.region
instanceid = args.instanceid
ssm_client = boto3.client('ssm', region_name=region)

file = open(args.commandfile, 'r')
script = file.read()

response = ssm_client.send_command(
            InstanceIds=[instanceid],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': [script]}, )
command_id = response['Command']['CommandId']

time.sleep(2)

output = ssm_client.get_command_invocation(
      CommandId=command_id,
      InstanceId=instanceid,
    )
print(output['StandardOutputContent'])

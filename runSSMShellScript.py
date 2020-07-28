#!/usr/bin/env python3
# Original Author @elitest
# This script is part of Redboto
# https://github.com/elitest/Redboto/

# This script runs commands on a SSM host
#

# Wishlist:
# Error checking?
# output to a file?

import boto3, argparse, botocore.exceptions, time, cmd

# Sets up the argument parser
argparser = argparse.ArgumentParser(description='Runs commands on SSM enabled hosts')
argparser.add_argument('--profile', default='default', help='The profile name in ~/.aws/credentials')
argparser.add_argument('--region', help='The region the instance is in.')
argparser.add_argument('instanceid', help='The InstanceID of the host with SSM installed and configured.')
argparser.add_argument('--commandfile', help='The file with commands to be run. If not specified a shell is emulated')
args = argparser.parse_args()

# Sets the profile for clients
if args.profile:
    boto3.setup_default_session(profile_name=args.profile)

region = args.region
instanceid = args.instanceid
# This starts the ssm client
ssm_client = boto3.client('ssm', region_name=region)

# This queries SSM for information to determine Windows or Linux
instanceInfo = ssm_client.describe_instance_information(Filters=[
        {
            'Key': 'InstanceIds',
            'Values': [
                instanceid
            ]
        },
    ])
# This should be Windows or Linux
platform = instanceInfo['InstanceInformationList'][0]['PlatformType']
if platform == 'Windows':
    document = 'AWS-RunPowerShellScript'
    prompt = 'PS AWS:\\> '
    badStatus = 'InProgress' 
    crlf = ''
elif platform == 'Linux':
    document = 'AWS-RunShellScript'
    prompt = 'you@%s:$ ' % args.instanceid
    badStatus = 'Pending'
    crlf = ' /\n'
else:
    print('Unknown platform, exiting')
    quit()

# This is the function that connects to SSM and runs the command
def runCommand(command):
    response = ssm_client.send_command(
                InstanceIds=[instanceid],
                DocumentName=document,
                Parameters={'commands': [command]}, )
    # Because the command takes a while to run we don't immediately receive a response
    # the CommandID allows us to check the status  
    command_id = response['Command']['CommandId']
    # This is a variable for the while loop.
    processed = 1
    time.sleep(1)

    # This loop checks the status and exits the loop once the status changes from Pending
    while processed:
        output = ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=instanceid,
        )
        time.sleep(1)
        # There may be other statuses to check for. These are the ones I've encountered.
        # There may be room here for better error checking
        if output['StatusDetails'] == 'Pending':
            pass
        elif output['StatusDetails'] == 'InProgress':
            pass
        else:
            # This breaks us out of the while loop
            processed = 0
        
    return(output['StandardOutputContent'])

# This runs the command from a file better for long bash scripts or stagers
if args.commandfile:
    file = open(args.commandfile, 'r')
    script = file.read()
    print(runCommand(script))
else:

    class CMDLoop(cmd.Cmd):
        intro = 'This isn\'t actually an interactive shell\n Ctrl+D to exit.'
        prompt = prompt
        def default(self, line):
            print(runCommand(line+crlf))
           #     return

        def do_EOF(self, line):
            return True

    CMDLoop().cmdloop()

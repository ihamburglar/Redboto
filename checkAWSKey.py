#!/usr/bin/env python3
#pip install boto3

#####
###
###  The purpose of this script is to gather some quick info from
###  AWS keys wittout making a lot of noise
###  Examples are key validity, groups, policies and MFA
###
#####

##### Output example:
#### This script checks the validity of AWS API keys
#### and provides some basic info about them.
#### What is the AWS Key ID? 
#### What is the AWS Key Secret? 
####     [*] Checking the key AKIA..............
#### The key: AKIA............... appears to be valid
#### The user "elitest" has the following groups:
####     [*] Group: IAM-example-group
#### Does the user: "elitest" have MFA configured?
####     [*] MFA Device is configured
#####

# TODO: take aws configs as a parameter
# TODO: optionally write to a file
# TODO: Put stuff in functions
# TODO: Doesn't enumerate role info currentlys
# TODO: May need to paginate for large permission sets?
# Pull requests accepted

#imports
from __future__ import print_function
import getpass, boto3, re
import argparse

parser = argparse.ArgumentParser(description='Checks AWS API keys.')
parser.add_argument('--profile')

args = parser.parse_args()

print('This script checks the validity of AWS API keys')
print('and provides some basic info about them.')
if args.profile:
    # Open iam client
    boto3.setup_default_session(profile_name=args.profile)
    iam_client = boto3.client('iam')
    # Open sts client
    sts_client = boto3.client('sts')
else:
    # Get creds
    access_id = getpass.getpass(prompt='What is the AWS Key ID? ')
    access_key = getpass.getpass(prompt='What is the AWS Key Secret? ')

    # Open iam client
    iam_client = boto3.client('iam', aws_access_key_id=access_id, aws_secret_access_key=access_key)
    # Open sts client
    sts_client = boto3.client('sts', aws_access_key_id=access_id, aws_secret_access_key=access_key) 


print("    [*] Checking the keys")

# Test if keys are valid by finding current user and if not valid, exit
try:
    user = iam_client.get_user()
    accountnum = sts_client.get_caller_identity()['Account']
    print('        [-] The keys appears to be valid for account: ' + accountnum )
except:
    print('        [-] The keys do not appear to be valid or do not have enough permissions to determine validity')
    exit()

# Get username associated with keys
username = user['User']['UserName']

# this loads a bunch of info about user from iam
details = iam_client.get_account_authorization_details(Filter=['User','Group'])

if details['GroupDetailList']:
    # this pulls out the group details
    grouplist = details['GroupDetailList']

    # this section lists the policies attached via groups
    print('The user \"' + username +'\" has the following policies attached because of group membership:')
    for group in grouplist:
        for policy in group['AttachedManagedPolicies']:
            policyname = policy['PolicyName']
            groupname = group['GroupName']
            print('    [*] The group ' + groupname + ' attches the following policy:')
            print('        [-] ' + policyname)

if details['UserDetailList']:
    for userdetails in details['UserDetailList']:
        # this section lists the policies attached directly and then specifies inline policies
        print('The user \"' + username +'\" has the following policies attached directly to their account:')
        for policy in userdetails['AttachedManagedPolicies']:
                policyname = policy['PolicyName']
                print('        [-] ' + policyname)

        #TODO there must be a better way
        try:
            # this section lists the policies attached directly
            print('The user \"' + username +'\" has the following inline policies directly to their account:')

            for policy in userdetails['UserPolicyList'][0]['PolicyDocument']['Statement'][0]['Action']:
                print('        [-] ' + policy)
        except KeyError:
            pass


# List if they have MFA device(s) configured
mfas = iam_client.list_mfa_devices(UserName=username)
if mfas['MFADevices'] == []:
    print("    [*] MFA Device is NOT configured")
else:
    for mfa in mfas['MFADevices']:
        print("    [*] MFA Device is configured")


#!/usr/bin/env python
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
# Pull requests accepted

#imports
from __future__ import print_function
import getpass, boto3

print('This script checks the validity of AWS API keys')
print('and provides some basic info about them.')

# Get creds
access_id = getpass.getpass(prompt='What is the AWS Key ID? ')
access_key = getpass.getpass(prompt='What is the AWS Key Secret? ')

print("    [*] Checking the key " +access_id)

# Open iam client
iam_client = boto3.client('iam', aws_access_key_id=access_id, aws_secret_access_key=access_key)

# Test if keys are valid by finding current user and if not valid, exit
try:
    user = iam_client.get_user()
    print('The key: ' + access_id + ' appears to be valid')
except:
    print('The key: ' + access_id + ' does not appear to be valid')
    exit()

# Get username associated with keys
username = user['User']['UserName']

# List policies
# Won't list any if none
policies = iam_client.list_user_policies(UserName=username)
for policy in policies['PolicyNames']:
    print('The user \"' + username +'\" has the following policies:')
    print(policy)
    print('[*] Policy: ' + policy['PolicyName'])

# List groups
# Won't list any if none
groups = iam_client.list_groups_for_user(UserName=username)
for group in groups['Groups']:
    print('The user \"' + username +'\" has the following groups:')
    print('    [*] Group: ' + group['GroupName'])

# List if they have MFA device(s) configured
# *Should* tell if they don't
mfas = iam_client.list_mfa_devices(UserName=username)
for mfa in mfas['MFADevices']:
    print('Does the user: \"' + username +'\" have MFA configured?')
    # Not 100% sure this does what I want in the case of no mfa
    # My guess is it will crash before giving an fpositive
    if mfa == "":
        print("    [*] MFA Device is NOT configured")
    else:
        print("    [*] MFA Device is configured")

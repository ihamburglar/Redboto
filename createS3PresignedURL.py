#!/usr/bin/env python3
# Original Author @elitest
# This script is part of Redboto
# https://github.com/elitest/Redboto/

# This script presigns URLs for S3 to access S3 URLs without API keys

# Wishlist:
# error checking
# Should we take URLs or just buckets and keys?

import boto3, argparse
from botocore.exceptions import ClientError


# Set up the argparser
argparser = argparse.ArgumentParser(description='This script presigns URLs for S3 to access S3 URLs without API keys.')
argparser.add_argument('bucket', help='The bucket which contains the file to be signed.')
argparser.add_argument('key', help='The path and name of the file to be signed.')
argparser.add_argument('--profile', default='default', help='The profile name in ~/.aws/credentials')
argparser.add_argument('--expiration', default=3600, help='The time in seconds from now that the link should expire.')
argparser.add_argument('--post', action='store_true', help='Makes the file writable with a post.')
args = argparser.parse_args()

# Pull out some variables from the argparser
bucket = args.bucket
expiration = args.expiration
key = args.key
profile = args.profile

# Set the profile and start the client
boto3.setup_default_session(profile_name=profile)
s3_client = boto3.client('s3')

def create_presigned_url(bucket_name, object_name, expiration=3600):
    # This function is for GET requests
    # It is borrowed almost completely from the boto3 documentation
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as error:
        print(error)
        return None

    return response


def create_presigned_post(bucket_name, object_name,
                          fields=None, conditions=None, expiration=3600):
    # This function is for POST requests
    # It is borrowed almost completely from the boto3 documentation
    """Generate a presigned URL S3 POST request to upload a file

    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     Fields=fields,
                                                     Conditions=conditions,
                                                     ExpiresIn=expiration)
    except ClientError as error:
        print(error)
        return None

    # The response contains the presigned URL and required fields
    return response

if args.post:
    # This is for when the user wants to do a writable signed url via POST
    url = create_presigned_post(bucket,key,None,None,expiration)
    # This is a demo python script to make posting a bit easier.
    postInfo = """import requests
fileContents = open('%s', 'rb').read()
files = {'file': ('%s', fileContents, 'multipart/form-data')}
http_response = requests.post('%s', files=files, data=%s)
# This will return true if it succeeded.
print(http_response.ok)

"""  % (url['fields']['key'], url['fields']['key'], url['url'], url['fields'])

    # This prints out the output
    print('============================================================')
    print('The following is a script that shows the example of how to')
    print('post data to S3 with only a few lines of python')
    print('Hopefully it will allow you to adapt it for other uses.')
    print('============================================================\n')
    print(postInfo)
else:
    # This is for when the user wants to just download files via GET
    url = create_presigned_url(bucket,key,expiration) 
    print(url)

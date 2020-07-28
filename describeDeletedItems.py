#!/usr/bin/env python3
# Original Author @elitest
# This script is part of Redboto
# https://github.com/elitest/Redboto/

# This script uses boto3 and texttable to print
# information about deleted items in an S3 bucket

# Wishlist:
# error checking
#   *When using an non-versioned bucket or there are no results.
# pagination

import boto3, argparse
from texttable import Texttable

argparser = argparse.ArgumentParser(description='Prints info about deleted items in s3 buckets and helps you download them.')
argparser.add_argument('bucket', help='The bucket with versioning enabled.')
args = argparser.parse_args()

bucket = args.bucket
client = boto3.client('s3')
response = client.list_object_versions(Bucket=bucket)


table = Texttable()
table.set_cols_align(["c", "c", "c", "c"])
table.set_cols_valign(["m", "m", "m", "m"])
table.set_cols_width([10,32,32,32])
table.header(["Owner", "Key", "VersionID", "LastModified"])
deletedKeys = []
for marker in response['DeleteMarkers']:
    deletedKeys.append(marker['Key']) 

for version in response['Versions']:
    if version['Key'] in deletedKeys:
        table.add_row([version['Owner']['DisplayName'] , version['Key'] , version['VersionId'],str(version['LastModified'])+" UTC"])


print(table.draw() + "\n")

print("If deleted objects were found you may be able to download them with the following command.")
print("Just remeber to include the correct Key and versionId.\n")
print("aws s3api get-object --bucket " + bucket + " --key <KEY> --version-id <VERSIONID> <OUTPUTFILE>")

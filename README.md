Redboto
==========

``Redboto`` is a collection of scripts that use the Amazon SDK for Python boto3 
to perform red team operations against the AWS API.

You can install the pre-requisite libraries with:

    $ pip install cryptography boto3 texttable

getEC2WinCreds.py
----------

If you have the right API key and .pem you can download and decrypt the intial Windows password for an instance.

getEC2Files.py
----------
Certainly the most complicated script of the bunch.  This script works well in conjunction with describeInstances.py which gives you metadata about instances in EC2.  With a very well permission API key you can exflitrate files from an EC2 instance.  The script takes a snapshot of a target volume, spins up an instance to attach to the volume, spins up and creates an S3 bucket, when the instance finishes launching it encrypts and copies the chosen files to the s3 bucket, the script pulls down from the S3 bucket and decrypts the files.  The script then tears down the infrastructure that it has created, leaving only logs behind, if enabled.

checkAWSKey.py
----------

Checks certain aspects of a key.  Valuable when checking if a key has been rotated or not,
or if it has things like MFA have been turned on.

createS3PresignedURL.py
----------
Creates S3 presigned URLs that can be read or written to with GET/POST requests without API keys(once signed).  This allows you to download or upload files from or to S3 without an AWS sdk or client.

describeTrailStatus.py
----------

This will tell you what regions have logging enabled.  If any.

describeInstances.py
----------
You can describe-instances with the AWS cli, however it returns ugly json.  This tool returns
a subset(but growing) of what describe-instances does, however it is much more readable.

describeDeletedItems.py
----------
describeDeletedItems.py lists items with delete markers and each of their corresponding versionIds.  Currently doesn't list all items in a bucket with more than 1000 versionIds.

describeUserData.py
----------
describeUserData.py lists the userData attribute of instances.  You can think of this as the startup script of the virtual machine.

describeConsoleScreenshot.py
----------
describeConsoleScreenshot.py iterates through instances in each region and prints the screenshots of each instance that is running.

runSSMShellScript.py
----------
runSSMShellScript.py runs a shell script on a Linux host or a PowerShell script on a Windows host via SSM if installed and configured.  The commands can be taken from a script or input directly via a semi-interactive shell.

Pull requests accepted!

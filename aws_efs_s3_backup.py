'''
Lambda Script to Backup EFS to S3 Bucket.
The lambda Script will create an EC2 instance and mount the EFS onto the EC2 instance. 
Compress the data present in EFS and transfer to an S3 bucket.

Maintainer: Rahul Divgan
https://github.com/rahuldivgan

Environment variables to be passed to the Lambda Function:

S3_BUCKET_NAME : S3 bucket to backup the EFS Data.
EFS_ID : EFS ID to be backed up.
AMI_ID : AMI ID you want to use for EC2 instance.
KEYPAIR_NAME : Keypair Name to use to create EC2 instance.

Required Lambda Permissions: 

Create/Run/Terminate EC2 Instance
Attach EFS
Read/Create/Update/Delete S3 Objects
'''

import boto3, time, os

region = 'us-west-2'
user_data  = """#!/bin/bash 
ec2_id=$(curl http://169.254.169.254/latest/meta-data/instance-id) 
cd /
mkdir data_dir
mount -t nfs4 -o vers=4.1 fs-{efs_id}.efs.eu-west-1.amazonaws.com:/ data_dir
tar czf data_dir_backup_$(date +%d-%m-%Y_%H-%M).tar.gz /data_dir
aws s3 mv data_dir_backup-*.tar.gz s3://{s3_bucket_name}/
aws ec2 terminate-instances --instance-ids $ec2_id --region us-west-2 """.format(s3_bucket_name=os.getenv('S3_BUCKET_NAME'), 
                                                                                 efs_id=os.getenv('EFS_ID'))

#Data
ami_id = os.getenv('AMI_ID')
keypair_name = os.getenv('KEYPAIR_NAME')

def lambda_handler(event, context):
    ec2 = boto3.client('ec2', region_name=region)
    new_instance = ec2.run_instances(
                        ImageId=ami_id,
                        MinCount=1,
                        MaxCount=1,
                        KeyName=keypair_name,
                        InstanceType='t2.micro',
                        SecurityGroups=['default'],
                        IamInstanceProfile={'Name':'EFSBackupRole'},
                        UserData=user_data)

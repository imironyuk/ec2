#!/usr/bin/python3
import boto3
from botocore.exceptions import ClientError
def my_func(a):
    global x
    x = security_group_id
    print(security_group_id)
SECURITY_GROUP_NAME = "Instans"
ec2 = boto3.client('ec2')
response = ec2.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
try:
    security_group_id = 0
    response = ec2.create_security_group(GroupName='BTCUSD',
                                         Description='DESCRIPTION',
                                         VpcId=vpc_id)
    security_group_id = response['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))
    data = ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 80,
             'ToPort': 80,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])



except ClientError as e:
    print(e)  
my_func(1)
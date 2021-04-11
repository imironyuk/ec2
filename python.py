#!/usr/bin/python3
import boto3
import time
import datetime
import os
from botocore.exceptions import ClientError

region_name = "us-east-1"
ec2 = boto3.resource('ec2')
client = boto3.client('ec2')
waiter = client.get_waiter('instance_status_ok')
instance = ec2.Instance('id')
email_send = 'daniilmironyuk@gmail.com'
response = client.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

btcusd_sg = client.describe_security_groups(GroupNames=['BTCUSD'])
if btcusd_sg != '':
    security_group_id = btcusd_sg.get('SecurityGroups', [{}])[0].get('GroupId', '')
    print('Security Group BTCUSD already exist %s in vpc %s.' % (security_group_id, vpc_id))
else:
    response_sg_id = client.create_security_group(GroupName='BTCUSD',
                                                  Description='DESCRIPTION',
                                                  VpcId=vpc_id)
    security_group_id = response_sg_id['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))
    data = client.authorize_security_group_ingress(
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

keypair_name = datetime.datetime.today().strftime("%d.%m.%Y_%H:%M_") + email_send + '.pem'
new_keypair = ec2.create_key_pair(KeyName=keypair_name)
with open(keypair_name, 'w') as file:
    file.write(new_keypair.key_material)
print('Create keypair in EC2 ' + keypair_name)
print('Create new EC2 instance')

new_instance = ec2.create_instances(
    ImageId='ami-0533f2ba8a1995cf9',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro',
    KeyName=keypair_name,
    SecurityGroupIds=[security_group_id])

print('Wait for instance will be running ' + new_instance[0].id)
new_instance[0].wait_until_running()
print('Load instance')
new_instance[0].load()
print('Wait for Instance state is OK')
waiter.wait(InstanceIds=[new_instance[0].id])

os.system('chmod 400 ' + keypair_name)
os.system('sed -i \'s/DOMAIN/' + new_instance[0].public_dns_name + '/\' script.sh')
os.system('scp -C -i ' + keypair_name + ' -o StrictHostKeyChecking=no script.sh ec2-user@' + new_instance[
    0].public_dns_name + ':/home/ec2-user/script.sh')
os.system('ssh -C -i ' + keypair_name + ' -o StrictHostKeyChecking=no ec2-user@' + new_instance[
    0].public_dns_name + ' sudo chmod +x /home/ec2-user/script.sh')
os.system('ssh -C -i ' + keypair_name + ' -o StrictHostKeyChecking=no ec2-user@' + new_instance[
    0].public_dns_name + ' sudo /home/ec2-user/script.sh')
os.system('sed -i \'s/' + new_instance[0].public_dns_name + '/DOMAIN/\' script.sh')

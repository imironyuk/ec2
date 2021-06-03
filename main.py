#!/usr/bin/python3
from sys import argv, exit
from threading import Thread, active_count
from boto3 import resource, client

if len (argv) > 1:
    count_instances_str = argv[1]
    count_instances = int(count_instances_str)
else:
    count_instances = 1

if len (argv) > 2:
    git_repo = argv[2]
else:
    git_repo = 'https://github.com/imironyuk/BTC.git'

resource = resource('ec2')
client = client('ec2')
waiter = client.get_waiter('instance_status_ok')

keypair_name_split_dot = git_repo.split(".")[1]
keypair_name_reverse = keypair_name_split_dot[::-1]
keypair_name_split_slash = keypair_name_reverse.split("/")[0]
keypair_name = keypair_name_split_slash[::-1]
user_data = ('''#!/bin/bash
yum install -y httpd git
systemctl start httpd
systemctl enable httpd &
cd /home/ec2-user
git clone %s repo
cat << EOF >"/home/ec2-user/reload.sh"
#!/bin/bash
cd /home/ec2-user/repo || cd /home/ec2-user
git pull || git clone %s repo
cp -a /home/ec2-user/repo/html/* /var/www/html/
systemctl reload httpd &
EOF
chmod +x /home/ec2-user/reload.sh
crontab -l 1> mycron
if ! grep -q 'reload.sh' mycron; then
echo "* * * * * /home/ec2-user/reload.sh" >> mycron
fi
crontab mycron
rm -rfv mycron''' % (git_repo, git_repo))

def sg_create():
  global security_group_id
  try:
     btcusd_sg = client.describe_security_groups(GroupNames=['BTCUSD'])
     security_group_id = btcusd_sg.get('SecurityGroups', [{}])[0].get('GroupId', '')
     print('[sg]       Security Group %s exist' % security_group_id)
  except:
     btcusd_sg = client.create_security_group(GroupName='BTCUSD',
                                                   Description='DESCRIPTION',
                                                   VpcId=vpc_id)
     security_group_id = btcusd_sg['GroupId']
     print('[sg]       Security Group Created %s' % security_group_id)
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

def keypair_create():
  try:
     keypair = client.describe_key_pairs(KeyNames=[keypair_name])
     print('[keypair]  Keypair %s exist' % keypair_name)
  except:
     new_keypair = resource.create_key_pair(KeyName=keypair_name)
     with open(keypair_name, 'w') as file:
         file.write(new_keypair.key_material)
     print('[keypair]  Created keypair %s' % keypair_name)

def create_instance(i):
  print('[instance] %s Create instance' % i)
  i = str(i)
  new_instance = resource.create_instances(
    ImageId='ami-0533f2ba8a1995cf9',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro',
    KeyName=keypair_name,
    UserData=user_data,
    SecurityGroupIds=[security_group_id],
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': '[' + keypair_name + '] ' + i
                },
            ]
        },
    ])
  i = int(i)
  print('[instance] %s Wait until running' % i)
  new_instance[0].wait_until_running()
  print('[instance] %s Load instance info' % i)
  new_instance[0].load()
  print('[instance] %s Wait for DNS will be avalible' % i)
  waiter.wait(InstanceIds=[new_instance[0].id])
  print('[instance] %s Load public DNS name' % i)
  print('[instance] %s Link to site on instance: http://%s' % (i, new_instance[0].public_dns_name))

print('[all]      Will created `%s` instances' % count_instances)
print('[all]      Website from `%s`' % git_repo)
print('[keypair]  SSH Keypair name `%s`' % keypair_name)

default_vpc = client.describe_vpcs()
vpc_id = default_vpc.get('Vpcs', [{}])[0].get('VpcId', '')
print('[vpc]      Default VPC ID is %s' % vpc_id)

sg_thread = Thread(target=keypair_create, args=())
keypair_thread = Thread(target=sg_create, args=())
sg_thread.start()
keypair_thread.start()
sg_thread.join()
keypair_thread.join()

i = 0
count_instances_minus_one = count_instances - 1
while True:
     th = Thread(target=create_instance, args=(i, ))
     th.start()
     if i == count_instances_minus_one :
        break
     i += 1

exit(0)

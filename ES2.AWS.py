#!/usr/bin/python3
import boto3

# Keypair name and instance name
keypair_name = 'BTCUSD'

# passing 'user_data' to the instance that used to run scripts after the instance starts
user_data = '''#!/bin/bash
yum install -y httpd git
systemctl start httpd
systemctl enable httpd &
cd /home/ec2-user
git clone https://github.com/imironyuk/BTCUSD.git
cat << EOF >"/home/ec2-user/reload.sh"
#!/bin/bash
cd /home/ec2-user/BTCUSD
git pull
cp -a /home/ec2-user/BTCUSD/btcmdi.com.xsph.ru/* /var/www/html/
systemctl reload httpd
EOF
chmod +x /home/ec2-user/reload.sh
crontab -l 1> mycron
if ! grep -q 'reload.sh' mycron; then
echo "* * * * * /home/ec2-user/reload.sh" >> mycron
fi
crontab mycron
rm -rfv mycron'''

resource = boto3.resource('ec2')
client = boto3.client('ec2')
waiter = client.get_waiter('instance_status_ok')

# Automatically gets default vpc_id
default_vpc = client.describe_vpcs()
vpc_id = default_vpc.get('Vpcs', [{}])[0].get('VpcId', '')
print('VPC ID is %s' % vpc_id)

# Idempotent Security Group verification (create if not exist or get security_group_id)
try:
     btcusd_sg = client.describe_security_groups(GroupNames=['BTCUSD'])
     security_group_id = btcusd_sg.get('SecurityGroups', [{}])[0].get('GroupId', '')
except:
     btcusd_sg = client.create_security_group(GroupName='BTCUSD',
                                                   Description='DESCRIPTION',
                                                   VpcId=vpc_id)
     security_group_id = btcusd_sg['GroupId']
     print('Security Group Created %s' % security_group_id)
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

# Idempotent SSH key pair verification (create if not exist and get Private Key)
try:
     keypair = client.describe_key_pairs(KeyNames=[keypair_name])
except:
     new_keypair = resource.create_key_pair(KeyName=keypair_name)
     with open(keypair_name, 'w') as file:
         file.write(new_keypair.key_material)
     print('Created keypair %s' % keypair_name)

# Create Instance t2.micro and waiting, for instance, to be available
print('Create new EC2 instance')
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
                    'Value': keypair_name
                },
            ]
        },
    ])

print('Wait for instance ' + new_instance[0].id + ' will be running')
new_instance[0].wait_until_running()
new_instance[0].load()
waiter.wait(InstanceIds=[new_instance[0].id])

# Displays the link that will be used to access our page
print('Link to site: http://%s' % new_instance[0].public_dns_name)

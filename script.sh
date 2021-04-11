#!/bin/bash

sudo yum install -y httpd git > /dev/null
sudo systemctl start httpd
sudo systemctl enable httpd
sudo usermod -a -G apache ec2-user
sudo chown -R ec2-user:apache /var/www
sudo chmod 2775 /var/www && find /var/www -type d -exec sudo chmod 2775 {} \;
find /var/www -type f -exec sudo chmod 0664 {} \;
git clone https://github.com/imironyuk/BTCUSD.git
cp -a ./BTCUSD/btcmdi.com.xsph.ru/* /var/www/html/
sudo systemctl reload httpd

cat << EOF >"/home/ec2-user/reload.sh"
#!/bin/bash
REAL_PWD="$PWD"
cd /home/ec2-user
git clone https://github.com/imironyuk/BTCUSD.git
sudo cp -a ./BTCUSD/btcmdi.com.xsph.ru/* /var/www/html/
sudo systemctl reload httpd
sudo rm -rf ./BTCUSD
cd "$REAL_PWD"
EOF

sudo chmod +x /home/ec2-user/reload.sh

crontab -l 1> mycron
if ! grep -q 'reload.sh' mycron; then
echo "* * * * * /home/ec2-user/reload.sh" >> mycron
fi
crontab mycron
rm -rfv mycron

echo -e "\nThe site with the BTC to USD exchange rate is located at the link: http://DOMAIN"
exit 0

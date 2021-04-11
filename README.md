
1. Install and configure AWS CLI according to the [official guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
2. Install Python 3.9 or older version
3. Install `boto3` and `botocore` python libraries

### Description of the script operation

1. Automatically gets default `vpc_id`
2. Idempotent Security Group verification (create if not exist or get `security_group_id`)
3. Create SSH key pair in AWS and get Private Key
4. Create Instance `t2.micro` with Security Group and Keypair that we created earlier
5. Expect the availability of Instance via SSH protocol which works on port `22`
6. Copy the `script.sh` to the instance and run it on it
   1. Install `httpd` and `git` (`httpd` - Apache web server)
   2. Enable and start `httpd` (enable - means that the `httpd` service will start  on the system startup)
   3. Clone GIT repository: https://github.com/imironyuk/BTCUSD.git which contains a web page that displays the `BTC/USD` rate and draws bars by the time
   4. Copy Web page with CSS modules to `/var/www/html/`
   5. Reload `httpd` service in order for the web page to be displayed on the Apache
   6. Create `reload.sh` script which pick up changes from GIT and refresh the page
   7. Setup `crontab` which will pick up changes from GIT every minute and refresh the page (runs `reload.sh` once per minute)
   8. Displays the link that will be used to access our page

### Contacts of the creator
- GitHub: [MDI](https://github.com/imironyuk)
- VK: [Daniil Mironuyk](https://vk.com/daniilmironyuk)
- Email: `daniilmironyuk@gmail.com`

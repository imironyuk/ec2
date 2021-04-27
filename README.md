
1. Install and configure AWS CLI according to the [official guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
2. Install Python 3.9 or older version
3. Install boto3 python librarys

### Description of the script operation

1. User_data for instace
2. Install httpd and git (httpd - Apache web server)
3. Enable and start httpd (enable - means that the httpd service will start on the system startup)
4. Create Instance `t2.micro` with Security Group and Keypair that we created earlier
5. Setup crontab (time-based job scheduler) which will pick up changes from GIT every minute and refresh the page (runs reload.sh once per minute)
6. `script.sh` to the instance and run it on it
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

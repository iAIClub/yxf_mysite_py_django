#!/bin/sh
#install nginx
sudo yum -y install nginx &&
sudo systemctl enable nginx &&
echo "check service:" &&
systemctl status nginx &&
#firewall
firewall-cmd --zone=public --add-port=80/tcp --permanent &&
firewall-cmd --reload &&
exit 0

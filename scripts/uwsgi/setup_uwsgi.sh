#!/bin/sh
#install uwsgi
sudo yum -y install python-devel &&
pip install uwsgi &&
#set as a server
sudo cp -f ./uwsgi.service /usr/lib/systemd/system/uwsgi.service &&
sudo chmod 754 /usr/lib/systemd/system/uwsgi.service &&
sudo systemctl enable uwsgi &&
echo "check service status:"
systemctl status uwsgi &&
#firewall
firewall-cmd --zone=public --add-port=9090/tcp --permanent &&
firewall-cmd --reload &&
exit 0

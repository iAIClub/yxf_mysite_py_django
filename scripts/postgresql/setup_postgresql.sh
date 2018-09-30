#!/bin/sh
#these commands are from official document. version 10
sudo yum install https://download.postgresql.org/pub/repos/yum/10/redhat/rhel-7-x86_64/pgdg-centos10-10-2.noarch.rpm &&
sudo yum install postgresql10 &&
sudo yum install postgresql10-server &&
/usr/pgsql-10/bin/postgresql-10-setup initdb &&
systemctl enable postgresql-10 &&
systemctl start postgresql-10 &&
#firewall
firewall-cmd --zone=public --add-port=5432/tcp --permanent &&
firewall-cmd --reload &&
echo "check service:" &&
systemctl status postgresql-10 &&
exit 0

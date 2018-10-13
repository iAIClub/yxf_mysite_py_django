yxf_mysite_py_django : 环境配置手动操作内容
=========================================================
（已包含在自动脚本的配置：1.更新软件源；2.开启防火墙端口；3.安装c/c++编译器gcc；4.安装服务）  
------------

### 项目维护:
使用git版本控制，开发环境为linux虚拟机（centos7，与服务器环境相似，安装中文输入法用于更新文档），所有开发以及git的更新完全在此系统进行，git项目根目录/opt/yxf_mysite_py_django，网站根目录/opt/yxf_mysite_py_django/mysite。  

### 上传到服务器:
VPS服务商vultr提供的centos系统默认关闭selinux，如此才能实现通过ssh远程登录，以及sftp远程文件。  
上传到同一位置/opt。    
第一次上传后使用项目中的脚本安装环境，后续上传只更新网站内容。  

### os:
关闭SELinux严格安全模式（累赘，若开启则服务软件很难拿到足够权限）：  
/etc/selinux/config：  
SELINUX=enforcing 改为 SELINUX=disabled  

### postgresql:
安装后默认生成一个OS用户postgres和一个数据库管理员postgres。  
默认数据库路径为/var/lib/pgsql/[version]/data/postgresql。  

1.切换到OS的postgres用户：   
 
	su postgres  
	
2.使用数据库的postgres进入psql，修改密码：  

	psql -U postgres  
	ALTER USER postgres WITH PASSWORD '[pwd]';  

3.修改配置文件，允许远程管理：  
配置文件/var/lib/pgsql/10/data/postgresql.conf：   
 
	listen_addresses = ‘localhost’ # 改为listen_addresses=’*’   
	
配置文件/var/lib/pgsql/10/data/pg_hba.conf 添加如下语句，同时其余全改为trust:  

	host    all            all      0.0.0.0/0（允许任何计算机远程）  trust  

新建数据库和用户：  

	CREATE DATABASE mysite;  
	CREATE USER mysite CREATEDB LOGIN PASSWORD '[pwd]';  
	GRANT ALL ON DATABASE mysite TO mysite;  
	  
### nginx:
配置文件/etc/nginx.conf设置user root;  
配置文件/etc/nginx.conf注释掉两个log文档路径，把server{}字段替换为include [mysiteroot]/nginx.conf  

### shadowsocks:
需要提前修改shandowsocks.json的IP到服务器的公网IP，以及密码。  
其余全部通过脚本完成  

### uwsgi:
全部通过脚本完成  

### django:
属于项目本身内容  

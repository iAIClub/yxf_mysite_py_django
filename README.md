yxf_mysite_py_django : 网站服务项目
=========================================================

------------

## 项目开发

项目主题：一整套网站  

开发环境：Linux（CentOS 7），python，django，postgresql，uwsgi，nginx  

编程语言：python  

git根目录：yxf_mysite_py_django  

git分支：master稳定版；develop开发版  

网站根目录：yxf_mysite_py_django/mysite（后面以./mysite表示）  

### 项目依赖  

python==2.7.x  

django==1.11.x  

pip>=18.x  

uwsgi==2.x  

ngnix==1.12.x  

postgresql==10.x  

yxf_mysite_py_django/requirments2.txt  

yxf_mysite_py_django/requirments3.txt  

### 项目架构

数据库服务器（提供数据持久化服务）：postgresql  

应用容器（MVC模式的容器，服务主体）：django（配置项：mysite/*+setting.cfg）,前端jquery+layui  

通用网关服务器（中间件，只提供通信转交服务）：uwsgi（配置项：/etc/uwsgi/*）  

网络服务器（HTTP及反向代理，只提供通信转交服务）：ngnix（配置项：/etc/nginx/*）  

#### Django内部架构

命令行工具：./mysite/manage.py  

网关配置：./mysite/mysite/uwsgi.py  

网站配置：./mysite/mysite/settings.py  

地址映射：./mysite/mysite/urls.py  

框架内建后台管理、用户认证、会话，以及其他中间件：admin&auth&session, other middlewares  

公共静态资源（js脚本、css样式、字体、图片等）：./mysite/static  

MVC子应用（提供具体服务功能的子模块）：./mysite/app_*  

MVC子应用后台管理相关：./mysite/app_*/admin.py&apps.py  

MVC子应用的前端模板：./mysite/templetes/app_*  

MVC子应用的视图（响应请求，提取、组合模板，后端渲染）：./mysite/app_*/views.py   

MVC子应用的模型（数据对象模型，定义的对象与数据库表一一对应）：./mysite/app_*/models.py   

#### Django项目开发   

0.项目维护:
	使用git版本控制，开发环境为linux虚拟机（centos7，与服务器环境相似，安装中文输入法用于更新文档），所有开发以及git的更新完全在此系统进行，git项目根目录/opt/yxf_mysite_py_django，网站根目录/opt/yxf_mysite_py_django/mysite。  
	VPS服务商提供的centos系统默认关闭selinux，如此才能实现通过ssh远程登录，以及sftp远程文件。（注意服务器的22端口是否被墙）  
	上传到同一位置/opt。  
	第一次上传后使用yxf_utils项目中的脚本安装环境，后续上传只更新网站内容。  

1.初始化工程:  

	进入想要放置django项目的路径：
	django startproject myproject——新建一个主项目作为一个完整的网站框架

2.随着项目进度逐步添加子应用:  

	进入项目路径：
	python manage.py startapp app_some——在django项目根目录新建app

3.随时更新数据模型:  

	默认使用sqlite3，可自己配置Mysql、Postgresql等数据库。

	进入项目路径：
	django提供数据表生成的专用命令，一些系统数据表必须通过命令自动生成：
	# Django 1.7 及以上的版本需要用以下命令
	python manage.py makemigrations
	python manage.py migrate

	数据导入导出：
	python manage.py dumpdata appname > appname.json
	python manage.py loaddata appname.json

4.创建管理员用户  

	python manage.py createsuperuser
	(input username)
	(input email)
	(input password)

5.目录结构：  

	manage.py
	/mysite——网站设置、url路由、网站管理程序  
	/log——日志记录、临时文件  
	/modules——偶尔用到的独立的后台离线程序，也包含一些需要单独启动的服务程序  
	/static——前端静态资源  
	/media——网站文件数据  
	/templetes——前端模板代码，模板与后端的交互：模板语言、url路由、render输入的变量  
	/app_*——各具体应用代码  
		/models——模型定义代码  
		/views——视图代码，request url->url route->views logic(get model & render templete)->response(data & html & redirect url)

------------

## 部署

服务器主机：VPS（ip，ssh（22），sftp（22），root管理员），提供HTTP网站服务  

上传：脚本上传master（屏蔽了数据、临时文件）  

已部署网站：[http://avata.cc]  

------------

## TODO

海外服务器被墙应急处理  

升级到python3.x版本  

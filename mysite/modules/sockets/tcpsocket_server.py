#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import socket
import threading
import re
import time
import datetime
import sys
import hashlib
import logging
import sqlite3
logging.basicConfig(level=logging.DEBUG)
dbconn = sqlite3.connect('tcpsocket_server.db')
dbcur = dbconn.cursor()


'''
部署于服务器但独立于网站的TcpServer，各个用户客户端之间可建立点对点TCP通信
服务器的TcpServer只监控状态以及提供通信桥梁（被动式服务，登录状态心跳，在线用户列表），不记录通信内容
网站的用户体系是Django控制的，有自己独立设定的密码加密算法，没办法在外部验证，只能另外构建一套账户体系
'''


class MyTcpServer:
    def __init__(self,myaddr):
        self.myaddr = myaddr
        dbconn = sqlite3.connect('tcpsocket_server.db')  # sqlite每个线程内都要单独建立连接使用
        dbcur = dbconn.cursor()
        dbcur.execute("select * from sqlite_master where type = 'table' and name = 'auth_user';")
        if not dbcur.fetchall():
            dbcur.execute("""
                CREATE TABLE auth_user (
                    username TEXT PRIMARY KEY NOT NULL,
                    password TEXT NOT NULL
                );  
                """)
            dbconn.commit()
        self.client_online = {}

    def handle_request(self,conn,addr):
        logging.info('Connection from %s:%s opened.' % addr)
        while True:  # 无数据阻塞在接收语句即是长连接，有数据即触发接收语句后续的语句，通过客户端的指令来关闭
            try:
                requestbytes = conn.recv(1024)  # 每次请求的内容不得超过1024字节
                request = requestbytes.decode('utf-8')
                logging.debug('收到客户端数据：'+str(request))
                # 客户端数据格式：command data1 data2
                try:
                    command = request.split(' ')[0]
                    # 登入
                    if command == 'login':
                        user = request.split(' ')[1]
                        passwd = request.split(' ')[2]
                        m = hashlib.md5()
                        m.update(bytes(passwd,encoding=('utf-8')))
                        realpasswd = m.hexdigest()
                        dbconn = sqlite3.connect('tcpsocket_server.db')  # sqlite每个线程内都要单独建立连接使用
                        dbcur = dbconn.cursor()
                        dbcur.execute("select * from auth_user where username='{0}' and password='{1}';".format(user,realpasswd))
                        dbres = dbcur.fetchall()
                        if dbres:
                            self.client_online[user] = {'username':user}  # 服务端记录登录信息
                            response=r"ok\r\n"  # 返回成功信息
                            conn.send(response.encode('utf-8'))
                        else:
                            response=r"error\r\n"
                            conn.send(response.encode('utf-8'))
                    # 简易的注册账号
                    elif command == 'register':
                        user = request.split(' ')[1]
                        passwd = request.split(' ')[2]
                        dbconn = sqlite3.connect('tcpsocket_server.db')  # sqlite每个线程内都要单独建立连接使用
                        dbcur = dbconn.cursor()
                        dbcur.execute("select * from auth_user where username='{0}';".format(user))
                        dbres = dbcur.fetchall()
                        if dbres:
                            response=r"error\r\n"
                            conn.send(response.encode('utf-8'))
                        else:
                            m = hashlib.md5()
                            m.update(bytes(passwd,encoding=('utf-8')))
                            realpasswd = m.hexdigest()
                            dbcur.execute("insert into auth_user values('{0}','{1}');".format(user,realpasswd))
                            dbconn.commit()
                            response=r"ok\r\n"  # 返回成功信息
                            conn.send(response.encode('utf-8'))
                    # 建立连接后的心跳
                    elif command == 'heartbeat':
                        user = request.split(' ')[1]
                        self.client_online[user]['last_ping'] = datetime.datetime.now()
                        response =r'heartback\r\n'  # 返回信息
                        conn.send(response.encode('utf-8'))
                    # 查询所有在线用户
                    elif command == 'alluser':
                        response =str(self.client_online)+r'\r\n'  # 返回字典字符串，客户端须eval()解读
                        conn.send(response.encode('utf-8'))
                    # 查询某个目标的IP与端口
                    elif command == 'query':
                        pass
                    # 登出
                    elif request == 'logout':
                        user = request.split(' ')[1]
                        del self.client_online[user]
                        conn.close()
                        logging.info('Connection from %s:%s closed.' % addr)
                    else:
                        response = r'error\r\n'
                        conn.send(response.encode('utf-8'))
                except:
                    response=r"error\r\n"
                    conn.send(response.encode('utf-8'))
            except:
                logging.info('Connection from %s:%s closed.' % addr)
                break

    def daemon_process(self):
        logging.info('run daemon_process...')
        while True:
            #logging.debug('------------daemon_process()')
            for user in list(self.client_online.keys()):
                if datetime.datetime.now() - self.client_online[user]['last_ping'] >= datetime.timedelta(minutes=5):
                    del self.client_online[user]  # 如果超过5分钟没有心跳，就移除
            #logging.debug(self.client_online)
            time.sleep(60)  # 间隔1分钟

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 关闭服务程序后立刻重置端口
        ip = self.myaddr.split(':')[0]
        port = int(self.myaddr.split(':')[1])
        s.bind((ip,port))
        s.listen(5)
        logging.info('run mytcpserver...')
        daemon = threading.Thread(target=self.daemon_process)  # 建立定时执行的守护线程
        daemon.setDaemon(True)
        daemon.start()
        while True:
            conn, addr = s.accept()  # 无请求时会阻塞，有新请求时会建立连接并向下执行，处理完成后再次阻塞
            t = threading.Thread(target=self.handle_request, args=(conn, addr))  # 为每一个请求新开一个线程（所有socket连接已就绪）
            t.setDaemon(True)  # 每个新开的线程都设置为守护线程，本服务关闭后所有的请求处理线程都会关闭，不会产生泄漏
            t.start()


if __name__ == '__main__':
    server = MyTcpServer('0.0.0.0:50008')
    server.run()

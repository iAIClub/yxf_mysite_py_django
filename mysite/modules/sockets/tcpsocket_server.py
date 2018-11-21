#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import socket
import threading
import re
import time
import logging
import SocketServer  # py2

logging.basicConfig(level=logging.NOTSET)  # 设置日志级别


'''
部署于服务器但独立于网站的TcpServer，各个用户客户端之间可直接建立点对点TCP通信
为各个用户初次登录和与其他人通信时提供地址解析服务（与客户端建立连接，返回通信目标的IP端口）
服务器的TcpServer只监控状态（登录状态心跳，在线用户列表），不记录通信内容，不参与双方通信
'''

#!!!!!!!!!!!!!使用这个封装过的类模拟http不行，浏览器访问一直pendding...。要换成原始的socket类
# class MyTcpServer(SocketServer.BaseRequestHandler):
#     def handle(self):
#         print(self.request,self.client_address,self.server)  # client_address like:('127.0.0.1', 38612)
#         conn = self.request
#         # conn.sendall("connected")
#         Flag = True
#         http_header = 'HTTP/1.1 200 OK\r\n'
#         http_header += 'Content-Type: text/html; charset=utf-8\r\n'
#         http_header += 'Access-Control-Allow-Origin: *\r\n'
#         http_header += '\r\n'
#         while Flag:
#             data = conn.recv(1024)
#             print(data)
#             # try:
#             conn.sendall(http_header + "<!DOCTYPE html><html><head></head><body></body></html>\r\n")
#             print(http_header + "<!DOCTYPE html><html><head></head><body></body></html>\r\n")
#             if data == 'logout':
#                 Flag = False
#             elif re.findall(r'^POST ',data):
#                 conn.sendall(http_protocol+http_head+"body")
#             elif re.findall(r'^heartbeat ',data):
#                 conn.sendall(http_protocol+http_head+"ok")
#             elif re.findall(r'^target ',data):
#                 target_username = data.split(' ')[1]
#             elif re.findall(r'^server ',data):
#                 pass
#             else:
#                 pass
#             except:
#                 conn.sendall("invalid")


def handle_request(conn,addr):
    logging.info('Connection from %s:%s opened.' % addr)
    http_header = 'HTTP/1.1 200 OK\r\n'
    http_header += 'Content-Type: text/html; charset=utf-8\r\n'
    http_header += 'Access-Control-Allow-Origin: *\r\n'
    http_header += '\r\n'
    http_chunked_ending = 'Transfer-Encoding: chunked'
    while True:  # 接受完数据后不关闭保持无限循环即是长连接，通过客户端的指令来关闭
        client_data = conn.recv(1024)
        logging.info(client_data)
        if len(client_data) >= 9:
            if client_data[0:9] == 'GET /exit':
                conn.close()
                logging.info('Connection from %s:%s closed.' % addr)
                break
        conn.sendall(http_header+'<!DOCTYPE html><html><head></head><body></body></html>')


def mytcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 关闭服务程序后立刻重置端口
    s.bind(('0.0.0.0', 8007))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_request, args=(conn, addr))  # 为每一个客户端建立的socket请求新开一个线程
        t.start()


if __name__ == '__main__':
    mytcp_server()

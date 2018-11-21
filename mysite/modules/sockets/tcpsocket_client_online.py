#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import socket
import requests
import SocketServer  # py2


def p2p_client_server():
    local_ip_port = ('127.0.0.1', 8007)
    s = socket.socket()
    s.bind(local_ip_port)
    s.listen(5)
    while True:
        conn, addr = s.accept()
        client_data = conn.recv(1024)
        s.close()


def p2p_client():
    remote_ip_port = ('127.0.0.1', 8007)
    c = socket.socket()
    c.connect(remote_ip_port)
    c.settimeout(5)
    c.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)  # 在客户端开启心跳维护
    while True:
        inp = raw_input('please input:')
        c.sendall(inp)
        if inp == 'GET /exit':
            break
        response = c.recv(1024)
        print(response)
    c.close()


if __name__ == '__main__':
    # p2p_client()
    res = requests.post('http://127.0.0.1:8007')
    print(res.text)

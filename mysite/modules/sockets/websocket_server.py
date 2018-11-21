#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import time
import sys
from twisted.internet import reactor, protocol
from twisted.python import log
from autobahn.twisted.websocket import WebSocketServerProtocol,WebSocketServerFactory


'''
通过监听独立端口实现WebSocket服务，需要额外开启
为什么不在Django内部实现？因为原生Django不支持，且插件也不好用，单独实现功能更全面
'''


class MyWebSocketProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {} bytes".format(len(payload)))
        else:
            print("Text message received: {}".format(payload.decode('utf8')))

        # echo back message verbatim
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {}".format(reason))


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    factory = WebSocketServerFactory()
    factory.protocol = MyWebSocketProtocol
    reactor.listenTCP(8007, factory)
    reactor.run()

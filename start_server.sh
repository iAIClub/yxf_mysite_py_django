#!/bin/sh

#goto project root
curpath=$(cd "$(dirname "$0")"; pwd)
cd $curpath

#websocket
cd ./mysite/modules/sockets
nohup python3 websocket_server.py > websocket_server.log 2>&1 &
cd $curpath

#tcpsocket
cd ./mysite/modules/sockets
nohup python3 tcpsocket_server.py > tcpsocket_server.log 2>&1 &
cd $curpath

#yixue
cd ..
cd ./yxf_yixue_py
nohup python3 server.py > server.log 2>&1 &
cd $curpath

echo "server is running in background"
echo "websocket:port=8007(public)"
echo "tcpsocket:port=50008(public)"
echo "yixue:port=8002(public)"
exit 0

#!/bin/sh
kill -9 $(netstat -npl | grep :8002 | awk '{print $7}' | awk -F"/" '{ print $1 }')
kill -9 $(netstat -npl | grep :8007 | awk '{print $7}' | awk -F"/" '{ print $1 }')
kill -9 $(netstat -npl | grep :50008 | awk '{print $7}' | awk -F"/" '{ print $1 }')
echo "server is stoped."
exit 0

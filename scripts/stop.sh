#!/bin/bash

PROJECT_PATH="/pjct/bbs"
GUNICORN_PID=`cat $PROJECT_PATH/gunicorn.pid`
kill -15 $GUNICORN_PID
NGINX_PID=`cat /run/nginx.pid`
kill $NGINX_PID

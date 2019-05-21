#!/bin/bash

PROJECT_PATH="/pjct/bbs"
echo "stop gunicorn..."
echo "stop nginx..."
$PROJECT_PATH/scripts/stop.sh   # 终止进程

sleep 1s  # 等待 1s 确保 gunicorn 已终止

echo "start gunicorn"
echo "start nginx"
$PROJECT_PATH/scripts/start.sh  # 启动 gunicorn和nginx

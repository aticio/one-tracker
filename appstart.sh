#!/bin/bash
cd /opt/one-tracker/
sudo chmod -R 777 *
pip3 install -r requirements.txt -U
kill -9 $(ps -ef | grep "python3 /opt/one-tracker/one-tracker.py" | grep -v grep | awk '{print $2}')
nohup python3 /opt/one-tracker/one-tracker.py > /dev/null 2> /dev/null < /dev/null &
#!/usr/bin/bash
uwsgi --ini start.ini --daemonize start.log
./task_close.py
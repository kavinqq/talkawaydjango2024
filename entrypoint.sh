#!/bin/bash

# 執行 migrations
python3 manage.py migrate
python3 manage.py collectstatic --noinput

# 啟動 gunicorn
exec gunicorn talkaway.wsgi:application --bind 0.0.0.0:8068
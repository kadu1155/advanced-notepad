@echo off
start "" /B python server.py
timeout /t 2 >nul
start msedge --app=http://127.0.0.1:8000

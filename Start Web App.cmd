@echo off
start "" http://localhost:35223
call iot\scripts\activate.bat &  python main.py & 


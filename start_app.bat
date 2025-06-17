@echo off
cd /d "C:\Users\Light Arena\Desktop\complaint_project"
start cmd /k "python manage.py runserver 0.0.0.0:8000"
timeout /t 5
cd /d "C:\Users\Light Arena\Downloads\ngrok-v3-stable-windows-amd64"
start cmd /k "ngrok http 8000"

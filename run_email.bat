@echo off
cd /d D:\django-project01

D:\django-project01\myvenv\Scripts\python.exe D:\django-project01\visitor_schedule\run_email.py >> D:\django-project01\log.txt 2>&1

@REM call .myvenv\Scripts\activate

@REM python run_email.py >> logs\email_%date:~0,4%%date:~5,2%%date:~8,2%.log 2>&1

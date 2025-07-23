@echo off
cd /d D:\visitor_schedule
call .myvenv\Scripts\activate

python run_email.py >> logs\email_%date:~0,4%%date:~5,2%%date:~8,2%.log 2>&1

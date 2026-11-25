@echo off
cd /d "%~dp0"
py -X utf8 -m src.main
exit /b %errorlevel%
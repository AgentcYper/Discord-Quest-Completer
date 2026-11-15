@echo off
title Soar Team - Quest Solver
chcp 65001 >nul
cd /d "%~dp0"
python main.py
if %errorlevel% neq 0 (
    echo.
    echo An error occurred running python main.py
    pause
)

@echo off
setlocal
cd /d "%~dp0"
title LLTools - English Learning Desktop Suite

echo ====================================================
echo      LLTools - English Learning Desktop Suite
echo ====================================================

REM 1. Kiem tra moi truong ao .venv
if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Khoi tao moi truong ao Python .venv...
    if exist "D:\Pinokio\bin\miniforge\python.exe" (
        "D:\Pinokio\bin\miniforge\python.exe" -m venv .venv
    ) else (
        python -m venv .venv
    )
)

REM 2. Kiem tra va cai dat thu vien requirements.txt
echo [2/3] Kiem tra va dong bo thu vien requirements.txt...
".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet

REM 3. Khoi chay Desktop Application
echo [3/3] Khoi dong ung dung LLTools...
".venv\Scripts\python.exe" main.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Chuong trinh gap loi khi khoi chay.
    pause
)

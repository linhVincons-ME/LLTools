@echo off
chcp 65001 > nul
title LLTools - English Learning Desktop Application

echo ====================================================
echo      🚀 LLTools - English Learning Desktop Suite
echo ====================================================

REM 1. Kiểm tra môi trường ảo .venv
if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Đang khởi tạo môi trường ảo Python .venv...
    if exist "D:\Pinokio\bin\miniforge\python.exe" (
        "D:\Pinokio\bin\miniforge\python.exe" -m venv .venv
    ) else (
        python -m venv .venv
    )
)

REM 2. Kiểm tra và cài đặt thư viện từ requirements.txt
echo [2/3] Đang đồng bộ thư viện từ requirements.txt vào .venv...
".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet

REM 3. Khởi chạy Desktop Application
echo [3/3] Đang khởi động cửa sổ ứng dụng LLTools Desktop...
".venv\Scripts\python.exe" main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ⚠️ Đã xảy ra lỗi khi khởi chạy. Vui lòng kiểm tra lại môi trường Python.
    pause
)

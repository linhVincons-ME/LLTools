@echo off
chcp 65001 > nul
title LLTools - English Learning Suite

echo ====================================================
echo      🚀 LLTools - English Learning Suite
echo ====================================================
echo Đang kiểm tra môi trường Python...

if exist ".venv\Scripts\python.exe" (
    echo Đang khởi chạy ứng dụng từ môi trường ảo .venv...
    ".venv\Scripts\python.exe" main.py
) else (
    echo Không tìm thấy .venv. Sử dụng python hệ thống...
    python main.py
)

pause

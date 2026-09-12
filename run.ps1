# PowerShell launcher for LLTools Desktop Application
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "     🚀 LLTools - English Learning Desktop Suite    " -ForegroundColor Yellow
Write-Host "====================================================" -ForegroundColor Cyan

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

# 1. Check/create venv
if (-not (Test-Path $venvPython)) {
    Write-Host "[1/3] Đang khởi tạo môi trường ảo Python .venv..." -ForegroundColor Yellow
    if (Test-Path "D:\Pinokio\bin\miniforge\python.exe") {
        & "D:\Pinokio\bin\miniforge\python.exe" -m venv (Join-Path $PSScriptRoot ".venv")
    } else {
        python -m venv (Join-Path $PSScriptRoot ".venv")
    }
}

# 2. Sync requirements.txt
Write-Host "[2/3] Đang đồng bộ thư viện từ requirements.txt..." -ForegroundColor Green
$reqFile = Join-Path $PSScriptRoot "requirements.txt"
& $venvPython -m pip install -r $reqFile --quiet

# 3. Launch Desktop Application
Write-Host "[3/3] Khởi động cửa sổ ứng dụng LLTools Desktop..." -ForegroundColor Cyan
& $venvPython (Join-Path $PSScriptRoot "main.py")

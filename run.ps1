# PowerShell launcher for LLTools
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "     🚀 LLTools - English Learning Suite            " -ForegroundColor Yellow
Write-Host "====================================================" -ForegroundColor Cyan

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    Write-Host "Kích hoạt môi trường ảo và khởi chạy ứng dụng..." -ForegroundColor Green
    & $venvPython (Join-Path $PSScriptRoot "main.py")
} else {
    Write-Host "Đang dùng python hệ thống..." -ForegroundColor Yellow
    python (Join-Path $PSScriptRoot "main.py")
}

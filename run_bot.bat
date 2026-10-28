@echo off
REM GiaThuocSi Bot - Windows Batch Script
REM Chạy bot tự động

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Kiểm tra virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo ============================================
    echo ERROR: Virtual environment not found
    echo ============================================
    echo.
    echo Please run these commands first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo   playwright install chromium
    echo.
    echo Then run this batch file again.
    echo.
    pause
    exit /b 1
)

REM Kích hoạt virtual environment
call venv\Scripts\activate.bat

REM Kiểm tra .env file
if not exist ".env" (
    echo ============================================
    echo ERROR: .env file not found!
    echo ============================================
    echo.
    echo Copy .env.example to .env and fill in your credentials:
    echo   copy .env.example .env
    echo.
    echo Then edit .env with:
    echo   - THUOCSI_USERNAME
    echo   - THUOCSI_PASSWORD
    echo.
    pause
    exit /b 1
)

REM Kiểm tra products.json
if not exist "products.json" (
    echo ============================================
    echo ERROR: products.json not found!
    echo ============================================
    echo.
    echo Please create products.json with your products list.
    echo.
    pause
    exit /b 1
)

REM Chạy bot
echo ============================================
echo GiaThuocSi Bot - Starting...
echo ============================================
echo.

python main.py

REM Nếu script kết thúc bất ngờ, hiển thị thông báo
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Bot exited with error code %errorlevel%
    echo.
    pause
)

exit /b %errorlevel%

@echo off
title URL Shortener with Bearer Token Authentication

echo ================================================
echo    URL Shortener with Bearer Token Auth
echo ================================================
echo.
echo Starting the service on http://localhost:8000
echo Bearer token authentication enabled for logging
echo.
echo Available endpoints:
echo   GET  /                    - Health check
echo   POST /shorturls           - Shorten a URL
echo   GET  /{shortcode}         - Redirect to original URL
echo   GET  /docs               - API documentation
echo.
echo Press Ctrl+C to stop the service
echo ================================================
echo.

cd /d "%~dp0"

REM Try to use virtual environment Python first, fallback to system Python
if exist "C:\Users\ICFAI TECH\Desktop\AffordMed\.venv\Scripts\python.exe" (
    echo Using virtual environment Python...
    "C:\Users\ICFAI TECH\Desktop\AffordMed\.venv\Scripts\python.exe" main.py
) else (
    echo Using system Python...
    python main.py
)

pause

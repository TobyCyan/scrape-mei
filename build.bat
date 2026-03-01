@echo off
REM Build script for ScrapeMei executable
REM This script creates a standalone .exe file

echo ========================================
echo ScrapeMei - Build Executable
echo ========================================
echo.

echo Running build script...
python build.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build successful!
    echo Executable location: dist\ScrapeMei.exe
    pause
) else (
    echo.
    echo Build failed! Check the error messages above.
    pause
    exit /b 1
)

@echo off
REM Build script for ScrapeMei executable
REM This script creates a standalone .exe file
REM
REM Alternative options:
REM   - build_folder.py: Creates folder distribution (more reliable)
REM   - python build.py --debug: Creates debug build with console

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
    echo.
    echo TIP: If .exe fails to start, try: python build_folder.py
    pause
) else (
    echo.
    echo Build failed! Check the error messages above.
    pause
    exit /b 1
)

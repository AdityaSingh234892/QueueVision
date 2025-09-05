@echo off
title Queue Management System
echo.
echo OpenCV Queue Management System
echo ==============================
echo.
echo Choose an option:
echo 1. Setup system (install dependencies)
echo 2. Run tests
echo 3. Run demo mode
echo 4. Run with camera
echo 5. Run with video file
echo 6. Exit
echo.
set /p choice=Enter your choice (1-6): 

if "%choice%"=="1" goto setup
if "%choice%"=="2" goto test
if "%choice%"=="3" goto demo
if "%choice%"=="4" goto camera
if "%choice%"=="5" goto video
if "%choice%"=="6" goto exit
goto invalid

:setup
echo.
echo Running setup...
python setup.py
pause
goto menu

:test
echo.
echo Running system tests...
python test_system.py
pause
goto menu

:demo
echo.
echo Starting demo mode...
echo Press Q to quit, H for help
python demo.py
pause
goto menu

:camera
echo.
echo Starting with camera...
echo Press Q to quit, S to save report, R to reset, H for help
python main.py
pause
goto menu

:video
echo.
set /p videopath=Enter path to video file: 
echo Starting with video file: %videopath%
python main.py --video "%videopath%"
pause
goto menu

:invalid
echo.
echo Invalid choice. Please try again.
pause

:menu
cls
goto start

:exit
echo.
echo Goodbye!
pause

:start
goto menu

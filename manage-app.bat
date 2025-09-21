@echo off
title SEWA Book Automation System - Windows Manager

:menu
cls
echo.
echo ========================================
echo   SEWA Book Automation System Manager
echo ========================================
echo.
echo 1. Start Application
echo 2. Stop Application
echo 3. Restart Application
echo 4. View Logs
echo 5. Rebuild and Start
echo 6. Check Status
echo 7. Open Application in Browser
echo 8. Backup Data
echo 9. Exit
echo.
set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto logs
if "%choice%"=="5" goto rebuild
if "%choice%"=="6" goto status
if "%choice%"=="7" goto open
if "%choice%"=="8" goto backup
if "%choice%"=="9" goto exit
goto menu

:start
echo.
echo 🚀 Starting SEWA Book Automation System...
docker-compose -f docker-compose.yml -f docker-compose.windows.yml up -d
if %errorLevel% == 0 (
    echo ✅ Application started successfully!
    echo 🌐 Access at: http://localhost:8501
) else (
    echo ❌ Failed to start application
)
echo.
pause
goto menu

:stop
echo.
echo 🛑 Stopping SEWA Book Automation System...
docker-compose -f docker-compose.yml -f docker-compose.windows.yml down
if %errorLevel% == 0 (
    echo ✅ Application stopped successfully!
) else (
    echo ❌ Failed to stop application
)
echo.
pause
goto menu

:restart
echo.
echo 🔄 Restarting SEWA Book Automation System...
docker-compose -f docker-compose.yml -f docker-compose.windows.yml restart
if %errorLevel% == 0 (
    echo ✅ Application restarted successfully!
    echo 🌐 Access at: http://localhost:8501
) else (
    echo ❌ Failed to restart application
)
echo.
pause
goto menu

:logs
echo.
echo 📋 Viewing application logs...
echo Press Ctrl+C to exit log view
echo.
docker-compose -f docker-compose.yml -f docker-compose.windows.yml logs -f
pause
goto menu

:rebuild
echo.
echo 🔨 Rebuilding and starting application...
docker-compose -f docker-compose.yml -f docker-compose.windows.yml down
docker-compose -f docker-compose.yml -f docker-compose.windows.yml up -d --build
if %errorLevel% == 0 (
    echo ✅ Application rebuilt and started successfully!
    echo 🌐 Access at: http://localhost:8501
) else (
    echo ❌ Failed to rebuild application
)
echo.
pause
goto menu

:status
echo.
echo 📊 Checking application status...
echo.
docker-compose -f docker-compose.yml -f docker-compose.windows.yml ps
echo.
echo 📁 Checking data files...
if exist "All_Sent_Records.xlsx" (
    echo ✅ All_Sent_Records.xlsx exists
) else (
    echo ❌ All_Sent_Records.xlsx missing
)
if exist "Duplicate_Transactions.xlsx" (
    echo ✅ Duplicate_Transactions.xlsx exists
) else (
    echo ❌ Duplicate_Transactions.xlsx missing
)
if exist "Failed_Transactions.xlsx" (
    echo ✅ Failed_Transactions.xlsx exists
) else (
    echo ❌ Failed_Transactions.xlsx missing
)
if exist "config.env" (
    echo ✅ config.env exists
) else (
    echo ❌ config.env missing
)
echo.
pause
goto menu

:open
echo.
echo 🌐 Opening application in browser...
start http://localhost:8501
echo ✅ Browser opened
echo.
pause
goto menu

:backup
echo.
echo 💾 Creating backup...
set backup_name=sewa-backup-%date:~-4,4%%date:~-10,2%%date:~-7,2%
echo Creating backup: %backup_name%
if not exist "backups" mkdir backups
powershell -Command "Compress-Archive -Path 'All_Sent_Records.xlsx', 'Duplicate_Transactions.xlsx', 'Failed_Transactions.xlsx', 'exports', 'uploads' -DestinationPath 'backups\%backup_name%.zip' -Force"
if %errorLevel% == 0 (
    echo ✅ Backup created successfully: backups\%backup_name%.zip
) else (
    echo ❌ Failed to create backup
)
echo.
pause
goto menu

:exit
echo.
echo 👋 Goodbye!
exit /b 0

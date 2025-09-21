@echo off
title SEWA Book Automation - Docker Desktop Setup

echo.
echo ========================================
echo   SEWA Book Automation System Setup
echo   Docker Desktop GUI Configuration
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as Administrator
) else (
    echo ❌ Please run this script as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo.
echo 📁 Creating project directories...
if not exist "data" mkdir data
if not exist "exports" mkdir exports
if not exist "exports\phone_validation" mkdir exports\phone_validation
if not exist "exports\address_validation" mkdir exports\address_validation
if not exist "exports\duplicate_detection" mkdir exports\duplicate_detection
if not exist "uploads" mkdir uploads

echo.
echo 📄 Creating initial files...
if not exist "All_Sent_Records.xlsx" echo. > All_Sent_Records.xlsx
if not exist "Duplicate_Transactions.xlsx" echo. > Duplicate_Transactions.xlsx
if not exist "Failed_Transactions.xlsx" echo. > Failed_Transactions.xlsx

echo.
echo 🔧 Checking Docker Desktop...
docker --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Docker Desktop is installed
) else (
    echo ❌ Docker Desktop is not installed or not in PATH
    echo Please install Docker Desktop for Windows first
    echo Download from: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

echo.
echo 🔧 Checking Docker Desktop status...
docker info >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Docker Desktop is running
) else (
    echo ⚠️  Docker Desktop may not be running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo.
echo 📝 Checking config.env file...
if exist "config.env" (
    echo ✅ config.env file exists
) else (
    echo ⚠️  config.env file not found!
    echo.
    echo Creating template config.env file...
    (
        echo # Twilio Configuration
        echo TWILIO_ACCOUNT_SID=your_account_sid_here
        echo TWILIO_AUTH_TOKEN=your_auth_token_here
        echo TWILIO_SMS_PHONE_NUMBER=+1234567890
        echo TWILIO_WHATSAPP_PHONE_NUMBER=+1234567890
        echo.
        echo # Google Maps API
        echo GOOGLE_MAPS_API_KEY=your_google_maps_api_key
        echo.
        echo # Enhanced Phone Validation ^(Optional^)
        echo ABSTRACT_API_KEY=your_abstract_api_key_here
    ) > config.env
    echo ✅ Template config.env created
)

echo.
echo 🔨 Building Docker image...
echo This may take 5-10 minutes...
docker build -t sewa-book-automation:latest .
if %errorLevel% == 0 (
    echo ✅ Docker image built successfully!
) else (
    echo ❌ Docker image build failed
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo ✅ Setup completed successfully!
echo.
echo 🎯 Next Steps:
echo.
echo 1. Open Docker Desktop
echo 2. Go to Containers tab
echo 3. Click "Run" button
echo 4. Select image: sewa-book-automation:latest
echo 5. Configure container settings:
echo.
echo    Container name: sewa-book-automation
echo    Ports: 8501:8501
echo.
echo    Environment Variables:
echo    STREAMLIT_SERVER_PORT=8501
echo    STREAMLIT_SERVER_ADDRESS=0.0.0.0
echo    PYTHONUNBUFFERED=1
echo.
echo    Volume Mounts:
echo    %CD%\data:/app/data
echo    %CD%\exports:/app/exports
echo    %CD%\All_Sent_Records.xlsx:/app/All_Sent_Records.xlsx
echo    %CD%\Duplicate_Transactions.xlsx:/app/Duplicate_Transactions.xlsx
echo    %CD%\Failed_Transactions.xlsx:/app/Failed_Transactions.xlsx
echo    %CD%\config.env:/app/config.env
echo    %CD%\uploads:/app/uploads
echo.
echo    Advanced Settings:
echo    Restart policy: Unless stopped
echo    Memory: 4GB
echo    CPU: 4 cores
echo.
echo 6. Click "Run"
echo 7. Access application at: http://localhost:8501
echo.
echo 📖 For detailed instructions, see:
echo    WINDOWS_DOCKER_DESKTOP_GUI.md
echo.
echo 🎉 Your SEWA Book Automation System is ready!
echo.
pause

@echo off
echo 🪟 Setting up SEWA Book Automation System for Windows...
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
echo 📁 Creating directories...
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
echo 🔧 Checking Docker installation...
docker --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Docker is installed
) else (
    echo ❌ Docker is not installed or not in PATH
    echo Please install Docker Desktop for Windows first
    echo Download from: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

echo.
echo 🔧 Checking Docker Compose...
docker-compose --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Docker Compose is available
) else (
    echo ❌ Docker Compose is not available
    echo Please ensure Docker Desktop is properly installed
    pause
    exit /b 1
)

echo.
echo 🔧 Checking WSL 2...
wsl --status >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ WSL 2 is available
) else (
    echo ⚠️  WSL 2 may not be properly configured
    echo Please ensure WSL 2 is installed and Docker Desktop is using it
)

echo.
echo 📝 Checking config.env file...
if exist "config.env" (
    echo ✅ config.env file exists
) else (
    echo ⚠️  config.env file not found!
    echo.
    echo Please create config.env with your API keys:
    echo.
    echo TWILIO_ACCOUNT_SID=your_account_sid_here
    echo TWILIO_AUTH_TOKEN=your_auth_token_here
    echo TWILIO_SMS_PHONE_NUMBER=+1234567890
    echo TWILIO_WHATSAPP_PHONE_NUMBER=+1234567890
    echo GOOGLE_MAPS_API_KEY=your_google_maps_api_key
    echo ABSTRACT_API_KEY=your_abstract_api_key_here
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
echo ✅ Setup completed!
echo.
echo 🚀 To run the application:
echo    docker-compose up -d
echo.
echo 🌐 Access the application at:
echo    http://localhost:8501
echo.
echo 📁 Data files will be available in:
echo    .\data\ - Application data
echo    .\exports\ - Validation results
echo    .\uploads\ - Uploaded files
echo    .\All_Sent_Records.xlsx - Sent records
echo    .\Duplicate_Transactions.xlsx - Duplicate transactions
echo    .\Failed_Transactions.xlsx - Failed transactions
echo.
echo 🛑 To stop the application:
echo    docker-compose down
echo.
echo 📖 For detailed instructions, see WINDOWS_DOCKER_SETUP.md
echo.
pause

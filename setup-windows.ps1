# PowerShell setup script for Windows Docker deployment
param(
    [switch]$SkipAdminCheck,
    [switch]$Force
)

Write-Host "🪟 Setting up SEWA Book Automation System for Windows..." -ForegroundColor Green
Write-Host ""

# Check if running as administrator
if (-not $SkipAdminCheck) {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $isAdmin) {
        Write-Host "❌ Please run this script as Administrator" -ForegroundColor Red
        Write-Host "Right-click PowerShell and select 'Run as administrator'" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ Running as Administrator" -ForegroundColor Green
}

# Function to create directory if it doesn't exist
function New-DirectoryIfNotExists {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Host "📁 Created directory: $Path" -ForegroundColor Cyan
    } else {
        Write-Host "📁 Directory exists: $Path" -ForegroundColor Gray
    }
}

# Function to create file if it doesn't exist
function New-FileIfNotExists {
    param([string]$Path, [string]$Content = "")
    if (-not (Test-Path $Path)) {
        New-Item -ItemType File -Path $Path -Force | Out-Null
        if ($Content) {
            Set-Content -Path $Path -Value $Content
        }
        Write-Host "📄 Created file: $Path" -ForegroundColor Cyan
    } else {
        Write-Host "📄 File exists: $Path" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "📁 Creating directories..." -ForegroundColor Yellow

# Create directories
New-DirectoryIfNotExists "data"
New-DirectoryIfNotExists "exports"
New-DirectoryIfNotExists "exports\phone_validation"
New-DirectoryIfNotExists "exports\address_validation"
New-DirectoryIfNotExists "exports\duplicate_detection"
New-DirectoryIfNotExists "uploads"

Write-Host ""
Write-Host "📄 Creating initial files..." -ForegroundColor Yellow

# Create initial files
New-FileIfNotExists "All_Sent_Records.xlsx"
New-FileIfNotExists "Duplicate_Transactions.xlsx"
New-FileIfNotExists "Failed_Transactions.xlsx"

Write-Host ""
Write-Host "🔧 Checking system requirements..." -ForegroundColor Yellow

# Check Docker installation
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "✅ Docker is installed: $dockerVersion" -ForegroundColor Green
    } else {
        throw "Docker not found"
    }
} catch {
    Write-Host "❌ Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Docker Desktop for Windows first" -ForegroundColor Yellow
    Write-Host "Download from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Docker Compose
try {
    $composeVersion = docker-compose --version 2>$null
    if ($composeVersion) {
        Write-Host "✅ Docker Compose is available: $composeVersion" -ForegroundColor Green
    } else {
        throw "Docker Compose not found"
    }
} catch {
    Write-Host "❌ Docker Compose is not available" -ForegroundColor Red
    Write-Host "Please ensure Docker Desktop is properly installed" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check WSL 2
try {
    $wslStatus = wsl --status 2>$null
    if ($wslStatus) {
        Write-Host "✅ WSL 2 is available" -ForegroundColor Green
    } else {
        Write-Host "⚠️  WSL 2 may not be properly configured" -ForegroundColor Yellow
        Write-Host "Please ensure WSL 2 is installed and Docker Desktop is using it" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  WSL 2 status could not be determined" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📝 Checking configuration..." -ForegroundColor Yellow

# Check config.env file
if (Test-Path "config.env") {
    Write-Host "✅ config.env file exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  config.env file not found!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Creating template config.env file..." -ForegroundColor Cyan
    
    $configContent = @"
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_SMS_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_PHONE_NUMBER=+1234567890

# Google Maps API
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Enhanced Phone Validation (Optional)
ABSTRACT_API_KEY=your_abstract_api_key_here
"@
    
    Set-Content -Path "config.env" -Value $configContent
    Write-Host "✅ Template config.env created" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  Please edit config.env with your actual API keys before running the application" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔧 Checking Docker Desktop status..." -ForegroundColor Yellow

# Check if Docker Desktop is running
try {
    $dockerInfo = docker info 2>$null
    if ($dockerInfo) {
        Write-Host "✅ Docker Desktop is running" -ForegroundColor Green
    } else {
        throw "Docker not running"
    }
} catch {
    Write-Host "⚠️  Docker Desktop may not be running" -ForegroundColor Yellow
    Write-Host "Please start Docker Desktop and try again" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 To run the application:" -ForegroundColor Cyan
Write-Host "   docker-compose up -d" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Access the application at:" -ForegroundColor Cyan
Write-Host "   http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "📁 Data files will be available in:" -ForegroundColor Cyan
Write-Host "   .\data\ - Application data" -ForegroundColor White
Write-Host "   .\exports\ - Validation results" -ForegroundColor White
Write-Host "   .\uploads\ - Uploaded files" -ForegroundColor White
Write-Host "   .\All_Sent_Records.xlsx - Sent records" -ForegroundColor White
Write-Host "   .\Duplicate_Transactions.xlsx - Duplicate transactions" -ForegroundColor White
Write-Host "   .\Failed_Transactions.xlsx - Failed transactions" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop the application:" -ForegroundColor Cyan
Write-Host "   docker-compose down" -ForegroundColor White
Write-Host ""
Write-Host "📖 For detailed instructions, see WINDOWS_DOCKER_SETUP.md" -ForegroundColor Cyan
Write-Host ""

# Optional: Ask if user wants to start the application
$startApp = Read-Host "Would you like to start the application now? (y/n)"
if ($startApp -eq "y" -or $startApp -eq "Y") {
    Write-Host ""
    Write-Host "🚀 Starting the application..." -ForegroundColor Green
    try {
        docker-compose up -d
        Write-Host "✅ Application started successfully!" -ForegroundColor Green
        Write-Host "🌐 Open your browser and go to: http://localhost:8501" -ForegroundColor Cyan
    } catch {
        Write-Host "❌ Failed to start the application" -ForegroundColor Red
        Write-Host "Please check the error messages above and try again" -ForegroundColor Yellow
    }
}

Write-Host ""
Read-Host "Press Enter to exit"

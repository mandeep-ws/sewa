# 🪟 Windows Docker Desktop Setup Guide

This guide explains how to run the SEWA Book Automation System on Windows using Docker Desktop.

## 📋 Prerequisites

### System Requirements
- **Windows 10/11** (64-bit)
- **8GB RAM minimum** (16GB recommended)
- **50GB free disk space**
- **WSL 2** (Windows Subsystem for Linux 2)

### Software Requirements
- **Docker Desktop for Windows**
- **Git for Windows** (optional, for version control)
- **PowerShell** or **Command Prompt**

## 🚀 Installation Steps

### Step 1: Install WSL 2

1. **Open PowerShell as Administrator**
2. **Run the following commands:**
   ```powershell
   # Enable WSL feature
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   
   # Enable Virtual Machine Platform
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   
   # Restart your computer
   Restart-Computer
   ```

3. **After restart, set WSL 2 as default:**
   ```powershell
   wsl --set-default-version 2
   ```

4. **Install a Linux distribution (Ubuntu recommended):**
   ```powershell
   wsl --install -d Ubuntu
   ```

### Step 2: Install Docker Desktop

1. **Download Docker Desktop for Windows:**
   - Go to: https://www.docker.com/products/docker-desktop/
   - Click "Download for Windows"

2. **Run the installer:**
   - Double-click `Docker Desktop Installer.exe`
   - Follow the installation wizard
   - **Important**: Check "Use WSL 2 instead of Hyper-V" if prompted

3. **Start Docker Desktop:**
   - Launch Docker Desktop from Start Menu
   - Complete the initial setup
   - Sign in to Docker Hub (optional)

4. **Verify Installation:**
   ```powershell
   docker --version
   docker-compose --version
   ```

### Step 3: Configure Docker Desktop

1. **Open Docker Desktop Settings:**
   - Right-click Docker Desktop system tray icon
   - Select "Settings"

2. **Configure Resources:**
   - Go to "Resources" → "Advanced"
   - Set **Memory**: 4GB minimum (8GB recommended)
   - Set **CPUs**: 2 minimum (4 recommended)
   - Click "Apply & Restart"

3. **Enable WSL 2 Integration:**
   - Go to "Resources" → "WSL Integration"
   - Enable "Use the WSL 2 based engine"
   - Enable integration with your Ubuntu distribution
   - Click "Apply & Restart"

## 📁 Project Setup

### Step 1: Download/Clone Project

**Option A: Using Git (Recommended)**
```powershell
# Clone the repository
git clone <your-repository-url>
cd sewa
```

**Option B: Download ZIP**
1. Download the project ZIP file
2. Extract to a folder (e.g., `C:\sewa`)
3. Open PowerShell in that directory

### Step 2: Run Setup Script

```powershell
# Make scripts executable (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run the setup script
.\setup-docker.sh
```

**Note**: If the script doesn't work, create directories manually:
```powershell
# Create directories manually
New-Item -ItemType Directory -Path "data" -Force
New-Item -ItemType Directory -Path "exports\phone_validation" -Force
New-Item -ItemType Directory -Path "exports\address_validation" -Force
New-Item -ItemType Directory -Path "exports\duplicate_detection" -Force
New-Item -ItemType Directory -Path "uploads" -Force

# Create initial files
New-Item -ItemType File -Path "All_Sent_Records.xlsx" -Force
New-Item -ItemType File -Path "Duplicate_Transactions.xlsx" -Force
New-Item -ItemType File -Path "Failed_Transactions.xlsx" -Force
```

### Step 3: Configure API Keys

1. **Create `config.env` file:**
   ```powershell
   # Create config file
   New-Item -ItemType File -Path "config.env" -Force
   ```

2. **Edit `config.env` with your credentials:**
   ```env
   # Twilio Configuration
   TWILIO_ACCOUNT_SID=your_account_sid_here
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_SMS_PHONE_NUMBER=+1234567890
   TWILIO_WHATSAPP_PHONE_NUMBER=+1234567890

   # Google Maps API
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key

   # Enhanced Phone Validation (Optional)
   ABSTRACT_API_KEY=your_abstract_api_key_here
   ```

## 🐳 Running the Application

### Step 1: Build and Start

```powershell
# Build and start the application
docker-compose up -d

# View logs
docker-compose logs -f
```

### Step 2: Access Application

1. **Open your web browser**
2. **Navigate to**: http://localhost:8501
3. **The SEWA Book Automation System should load**

### Step 3: Verify Data Persistence

Check that files are created in your project directory:
- `All_Sent_Records.xlsx`
- `Duplicate_Transactions.xlsx`
- `Failed_Transactions.xlsx`
- `exports/` folder with validation results

## 🛠️ Windows-Specific Commands

### PowerShell Commands
```powershell
# Start application
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f sewa-app

# Restart application
docker-compose restart

# Rebuild and start
docker-compose up -d --build

# Check container status
docker-compose ps

# Execute commands in container
docker-compose exec sewa-app bash
```

### Command Prompt Commands
```cmd
# Start application
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f sewa-app
```

## 🔧 Windows-Specific Configuration

### File Paths
- **Project Directory**: `C:\sewa\` (or your chosen location)
- **Data Files**: Available in the project directory
- **Docker Data**: Stored in WSL 2 filesystem

### Network Configuration
- **Application Port**: 8501
- **Access URL**: http://localhost:8501
- **Firewall**: Windows Firewall may prompt for permission

### Performance Optimization

1. **Docker Desktop Settings:**
   - Increase memory allocation to 8GB
   - Enable file sharing for your project directory
   - Use WSL 2 backend

2. **Windows Settings:**
   - Disable Windows Defender real-time scanning for project folder
   - Add project folder to Windows Defender exclusions

3. **WSL 2 Optimization:**
   ```powershell
   # Create .wslconfig file in your user directory
   # C:\Users\[YourUsername]\.wslconfig
   ```
   ```ini
   [wsl2]
   memory=8GB
   processors=4
   swap=2GB
   ```

## 🐛 Windows-Specific Troubleshooting

### Common Issues

#### 1. WSL 2 Not Installed
```powershell
# Check WSL version
wsl --list --verbose

# If WSL 1, convert to WSL 2
wsl --set-version Ubuntu 2
```

#### 2. Docker Desktop Won't Start
- **Check WSL 2**: Ensure WSL 2 is running
- **Restart Docker Desktop**: Close and reopen Docker Desktop
- **Check Windows Features**: Ensure Hyper-V and Virtual Machine Platform are enabled

#### 3. Port Already in Use
```powershell
# Check what's using port 8501
netstat -ano | findstr :8501

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

#### 4. Permission Issues
```powershell
# Run PowerShell as Administrator
# Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Fix file permissions
icacls "C:\sewa" /grant Everyone:F /T
```

#### 5. File Access Issues
- **Enable file sharing** in Docker Desktop settings
- **Add project folder** to Docker Desktop file sharing
- **Check Windows Defender** exclusions

#### 6. Slow Performance
- **Increase Docker memory** allocation
- **Use SSD storage** for better performance
- **Close unnecessary applications**

### Debug Commands
```powershell
# Check Docker status
docker info

# Check WSL status
wsl --status

# Check container logs
docker-compose logs sewa-app

# Check system resources
Get-ComputerInfo | Select-Object TotalPhysicalMemory, CsProcessors
```

## 📊 Windows Performance Tips

### 1. Resource Allocation
- **RAM**: Allocate 8GB to Docker Desktop
- **CPU**: Allocate 4 cores to Docker Desktop
- **Storage**: Use SSD for better I/O performance

### 2. Windows Defender
```powershell
# Add exclusions for better performance
Add-MpPreference -ExclusionPath "C:\sewa"
Add-MpPreference -ExclusionProcess "docker.exe"
Add-MpPreference -ExclusionProcess "com.docker.backend.exe"
```

### 3. WSL 2 Optimization
```powershell
# Create .wslconfig in user directory
# C:\Users\[YourUsername]\.wslconfig
```
```ini
[wsl2]
memory=8GB
processors=4
swap=2GB
localhostForwarding=true
```

## 🔄 Backup and Restore

### Backup Data
```powershell
# Create backup
Compress-Archive -Path "All_Sent_Records.xlsx", "Duplicate_Transactions.xlsx", "Failed_Transactions.xlsx", "exports", "uploads" -DestinationPath "sewa-backup-$(Get-Date -Format 'yyyyMMdd').zip"
```

### Restore Data
```powershell
# Extract backup
Expand-Archive -Path "sewa-backup-20231201.zip" -DestinationPath "."
```

## 🎯 Windows-Specific Features

### 1. Windows Service Integration
```powershell
# Create Windows service (optional)
sc create "SEWA-App" binPath="docker-compose up -d" start=auto
```

### 2. Windows Task Scheduler
- Create scheduled tasks for automatic backups
- Set up monitoring tasks

### 3. Windows Event Logs
- Monitor Docker Desktop logs
- Track application performance

## 📞 Windows Support

### Getting Help
1. **Docker Desktop Logs**: View in Docker Desktop GUI
2. **Windows Event Viewer**: Check system logs
3. **WSL Logs**: `wsl --list --verbose`
4. **Application Logs**: `docker-compose logs -f sewa-app`

### Useful Windows Tools
- **Docker Desktop GUI**: Visual container management
- **Windows Terminal**: Better terminal experience
- **WSL 2**: Linux environment integration
- **PowerShell**: Advanced command-line interface

## 🎉 Success Checklist

- [ ] WSL 2 installed and configured
- [ ] Docker Desktop installed and running
- [ ] Project files downloaded and configured
- [ ] `config.env` created with API keys
- [ ] Application accessible at http://localhost:8501
- [ ] Data files persisting in project directory
- [ ] All features working (phone validation, messaging, etc.)

---

**🎉 Your SEWA Book Automation System is now ready to run on Windows with Docker Desktop!**

## 📋 Quick Reference

| Task | Command |
|------|---------|
| Start App | `docker-compose up -d` |
| Stop App | `docker-compose down` |
| View Logs | `docker-compose logs -f` |
| Restart | `docker-compose restart` |
| Rebuild | `docker-compose up -d --build` |
| Access App | http://localhost:8501 |

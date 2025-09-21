# 🛠️ Windows Troubleshooting Guide

This guide helps you resolve common issues when running the SEWA Book Automation System on Windows with Docker Desktop.

## 🚨 Common Issues and Solutions

### 1. Docker Desktop Won't Start

#### Symptoms:
- Docker Desktop fails to start
- "Docker Desktop failed to start" error
- WSL 2 integration issues

#### Solutions:

**Check WSL 2 Installation:**
```powershell
# Check WSL version
wsl --list --verbose

# If WSL 1, convert to WSL 2
wsl --set-version Ubuntu 2
```

**Enable Required Windows Features:**
```powershell
# Run as Administrator
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

**Restart Docker Desktop:**
1. Close Docker Desktop completely
2. End all Docker processes in Task Manager
3. Restart Docker Desktop
4. Wait for full startup (green icon in system tray)

### 2. Port Already in Use (8501)

#### Symptoms:
- "Port 8501 is already in use" error
- Application won't start

#### Solutions:

**Find and Kill Process:**
```powershell
# Find process using port 8501
netstat -ano | findstr :8501

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Change Port:**
Edit `docker-compose.windows.yml`:
```yaml
ports:
  - "8502:8501"  # Change 8501 to 8502
```

### 3. Permission Issues

#### Symptoms:
- "Access denied" errors
- Files not created/updated
- Docker volume mount issues

#### Solutions:

**Run as Administrator:**
```powershell
# Right-click PowerShell and "Run as administrator"
```

**Fix File Permissions:**
```powershell
# Grant full access to project folder
icacls "C:\sewa" /grant Everyone:F /T

# Or use PowerShell
Get-ChildItem -Path "C:\sewa" -Recurse | Set-Acl -AclObject (Get-Acl "C:\sewa")
```

**Docker Desktop File Sharing:**
1. Open Docker Desktop Settings
2. Go to "Resources" → "File Sharing"
3. Add your project directory (e.g., `C:\sewa`)
4. Click "Apply & Restart"

### 4. WSL 2 Issues

#### Symptoms:
- "WSL 2 installation is incomplete" error
- Docker can't connect to WSL 2
- Slow performance

#### Solutions:

**Update WSL 2:**
```powershell
# Update WSL 2
wsl --update

# Set WSL 2 as default
wsl --set-default-version 2
```

**Install Linux Distribution:**
```powershell
# Install Ubuntu
wsl --install -d Ubuntu

# Or install from Microsoft Store
```

**WSL 2 Configuration:**
Create `C:\Users\[YourUsername]\.wslconfig`:
```ini
[wsl2]
memory=8GB
processors=4
swap=2GB
localhostForwarding=true
```

### 5. Application Won't Load

#### Symptoms:
- Browser shows "This site can't be reached"
- Connection refused errors
- Application not accessible

#### Solutions:

**Check Container Status:**
```powershell
# Check if container is running
docker-compose ps

# Check container logs
docker-compose logs sewa-app
```

**Verify Port Binding:**
```powershell
# Check if port is listening
netstat -an | findstr :8501
```

**Restart Application:**
```powershell
# Stop and start
docker-compose down
docker-compose up -d
```

### 6. Slow Performance

#### Symptoms:
- Application loads slowly
- High CPU/memory usage
- Delayed responses

#### Solutions:

**Increase Docker Resources:**
1. Open Docker Desktop Settings
2. Go to "Resources" → "Advanced"
3. Increase Memory to 8GB
4. Increase CPUs to 4
5. Click "Apply & Restart"

**Windows Defender Exclusions:**
```powershell
# Add exclusions
Add-MpPreference -ExclusionPath "C:\sewa"
Add-MpPreference -ExclusionProcess "docker.exe"
Add-MpPreference -ExclusionProcess "com.docker.backend.exe"
```

**WSL 2 Optimization:**
```ini
# C:\Users\[YourUsername]\.wslconfig
[wsl2]
memory=8GB
processors=4
swap=2GB
```

### 7. File Access Issues

#### Symptoms:
- Files not found
- Data not persisting
- Export files not created

#### Solutions:

**Check Volume Mounts:**
```powershell
# Verify files exist
dir All_Sent_Records.xlsx
dir exports
dir uploads
```

**Fix Docker Volume Permissions:**
```powershell
# Recreate with proper permissions
docker-compose down
docker-compose up -d --force-recreate
```

**Check File Sharing:**
1. Docker Desktop Settings
2. "Resources" → "File Sharing"
3. Ensure project directory is listed
4. Restart Docker Desktop

### 8. API Key Issues

#### Symptoms:
- "Invalid API key" errors
- Twilio connection failures
- Google Maps API errors

#### Solutions:

**Verify config.env:**
```powershell
# Check file exists and has content
type config.env
```

**Check API Key Format:**
```env
# Ensure no extra spaces or quotes
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
```

**Test API Keys:**
```powershell
# Test Twilio connection
docker-compose exec sewa-app python -c "from twilio.rest import Client; print('Twilio OK')"
```

### 9. Memory Issues

#### Symptoms:
- "Out of memory" errors
- Container crashes
- System slowdown

#### Solutions:

**Increase Docker Memory:**
1. Docker Desktop Settings
2. "Resources" → "Advanced"
3. Set Memory to 8GB or more
4. Restart Docker Desktop

**Close Other Applications:**
- Close unnecessary programs
- Free up system memory
- Restart Windows if needed

### 10. Network Issues

#### Symptoms:
- Can't connect to external APIs
- Twilio/Google Maps API failures
- Internet connectivity issues

#### Solutions:

**Check Internet Connection:**
```powershell
# Test connectivity
ping google.com
ping api.twilio.com
```

**Check Firewall:**
1. Windows Defender Firewall
2. Allow Docker Desktop through firewall
3. Allow port 8501 through firewall

**Proxy Settings:**
If using corporate proxy:
1. Docker Desktop Settings
2. "Resources" → "Proxies"
3. Configure proxy settings

## 🔧 Diagnostic Commands

### System Information
```powershell
# Check Windows version
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion

# Check available memory
Get-ComputerInfo | Select-Object TotalPhysicalMemory

# Check Docker version
docker --version
docker-compose --version
```

### Docker Status
```powershell
# Check Docker status
docker info

# Check running containers
docker ps

# Check container logs
docker-compose logs sewa-app

# Check container resource usage
docker stats
```

### WSL Status
```powershell
# Check WSL status
wsl --status

# List WSL distributions
wsl --list --verbose

# Check WSL version
wsl --version
```

### Network Diagnostics
```powershell
# Check port usage
netstat -ano | findstr :8501

# Test connectivity
Test-NetConnection -ComputerName localhost -Port 8501

# Check DNS resolution
nslookup api.twilio.com
```

## 📞 Getting Help

### Log Collection
```powershell
# Collect all logs
docker-compose logs > docker-logs.txt
docker info > docker-info.txt
wsl --status > wsl-status.txt
```

### System Information
```powershell
# Collect system info
Get-ComputerInfo > system-info.txt
Get-Process | Where-Object {$_.ProcessName -like "*docker*"} > docker-processes.txt
```

### Contact Information
1. **Check Docker Desktop Logs**: View in Docker Desktop GUI
2. **Windows Event Viewer**: Check system logs
3. **Application Logs**: `docker-compose logs -f sewa-app`
4. **WSL Logs**: `wsl --list --verbose`

## 🎯 Quick Fixes

### Complete Reset
```powershell
# Stop everything
docker-compose down
docker system prune -a

# Restart Docker Desktop
# Restart Windows

# Rebuild and start
docker-compose up -d --build
```

### Fresh Installation
```powershell
# Remove all Docker data
docker system prune -a --volumes

# Reinstall Docker Desktop
# Run setup scripts again
```

### Emergency Recovery
```powershell
# Backup data
Compress-Archive -Path "All_Sent_Records.xlsx", "exports", "uploads" -DestinationPath "emergency-backup.zip"

# Reset Docker
docker-compose down
docker system prune -a

# Restart from scratch
docker-compose up -d --build
```

---

**🆘 If you're still having issues, please collect the diagnostic information above and contact support.**

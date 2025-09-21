# 🪟 Windows Docker Desktop GUI Setup Guide

This guide explains how to run the SEWA Book Automation System on Windows using Docker Desktop's graphical interface.

## 📋 Prerequisites

- **Windows 10/11** (64-bit)
- **Docker Desktop for Windows** installed and running
- **WSL 2** enabled
- Your API keys and credentials

## 🚀 Step-by-Step Setup

### Step 1: Prepare Your Project

#### Create Project Directory:
```cmd
# Create project folder
mkdir C:\sewa
cd C:\sewa
```

#### Download/Copy Project Files:
- Copy all your project files to `C:\sewa`
- Ensure you have: `Dockerfile`, `requirements.txt`, `app.py`, `modules/` folder, etc.

#### Create Data Directories:
```cmd
# Create required directories
mkdir data
mkdir exports
mkdir exports\phone_validation
mkdir exports\address_validation
mkdir exports\duplicate_detection
mkdir uploads
```

#### Create Initial Files:
```cmd
# Create empty Excel files
echo. > All_Sent_Records.xlsx
echo. > Duplicate_Transactions.xlsx
echo. > Failed_Transactions.xlsx
```

#### Create Configuration File:
Create `config.env` with your API keys:
```env
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_SMS_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_PHONE_NUMBER=+1234567890
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
ABSTRACT_API_KEY=your_abstract_api_key_here
```

### Step 2: Build Docker Image

#### Using Docker Desktop GUI:

1. **Open Docker Desktop**
2. **Navigate to Images tab**
3. **Click "Build" button**
4. **Configure build settings:**
   ```
   Build context: C:\sewa
   Dockerfile: Dockerfile
   Image name: sewa-book-automation
   Tag: latest
   ```
5. **Click "Build"**
6. **Wait for build to complete** (this may take 5-10 minutes)

#### Alternative: Command Line Build:
```cmd
# Open Command Prompt in project directory
cd C:\sewa
docker build -t sewa-book-automation:latest .
```

### Step 3: Run Container

#### Using Docker Desktop GUI:

1. **Go to Containers tab**
2. **Click "Run" button**
3. **Select image**: `sewa-book-automation:latest`
4. **Configure container settings:**

#### Basic Configuration:
```
Container name: sewa-book-automation
Ports: 8501:8501
```

#### Environment Variables:
```
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
PYTHONUNBUFFERED=1
TZ=America/New_York
```

#### Volume Mounts (Windows Paths):
```
C:\sewa\data:/app/data
C:\sewa\exports:/app/exports
C:\sewa\All_Sent_Records.xlsx:/app/All_Sent_Records.xlsx
C:\sewa\Duplicate_Transactions.xlsx:/app/Duplicate_Transactions.xlsx
C:\sewa\Failed_Transactions.xlsx:/app/Failed_Transactions.xlsx
C:\sewa\config.env:/app/config.env
C:\sewa\uploads:/app/uploads
```

#### Advanced Settings:
```
Restart policy: Unless stopped
Memory: 4GB
CPU: 4 cores
```

5. **Click "Run"**

### Step 4: Access Application

1. **Wait for container to start** (check status in Containers tab)
2. **Open your web browser**
3. **Navigate to**: http://localhost:8501
4. **The SEWA Book Automation System should load**

## 🎯 Windows-Specific Configuration

### Docker Desktop Settings

#### Enable File Sharing:
1. **Open Docker Desktop Settings**
2. **Go to "Resources" → "File Sharing"**
3. **Add**: `C:\sewa`
4. **Click "Apply & Restart"**

#### WSL 2 Integration:
1. **Go to "Resources" → "WSL Integration"**
2. **Enable "Use the WSL 2 based engine"**
3. **Enable integration with your Ubuntu distribution**
4. **Click "Apply & Restart"**

#### Resource Allocation:
1. **Go to "Resources" → "Advanced"**
2. **Set Memory**: 8GB
3. **Set CPUs**: 4
4. **Click "Apply & Restart"**

### Windows Defender Exclusions

```powershell
# Run PowerShell as Administrator
Add-MpPreference -ExclusionPath "C:\sewa"
Add-MpPreference -ExclusionProcess "docker.exe"
Add-MpPreference -ExclusionProcess "com.docker.backend.exe"
```

## 🛠️ Container Management

### Using Docker Desktop GUI

#### Start Container:
1. **Go to Containers tab**
2. **Find**: `sewa-book-automation`
3. **Click the "Play" button** ▶️

#### Stop Container:
1. **Go to Containers tab**
2. **Find**: `sewa-book-automation`
3. **Click the "Stop" button** ⏹️

#### Restart Container:
1. **Go to Containers tab**
2. **Find**: `sewa-book-automation`
3. **Click the "Restart" button** 🔄

#### View Logs:
1. **Go to Containers tab**
2. **Click on**: `sewa-book-automation`
3. **Go to "Logs" tab**
4. **View real-time logs**

#### View Stats:
1. **Go to Containers tab**
2. **Click on**: `sewa-book-automation`
3. **Go to "Stats" tab**
4. **Monitor CPU, Memory, Network usage**

#### Edit Container:
1. **Go to Containers tab**
2. **Find**: `sewa-book-automation`
3. **Click the "Settings" button** ⚙️
4. **Modify settings as needed**
5. **Click "Save"**

### Using Windows Command Line

```cmd
# Start container
docker start sewa-book-automation

# Stop container
docker stop sewa-book-automation

# Restart container
docker restart sewa-book-automation

# View logs
docker logs -f sewa-book-automation

# Check status
docker ps
```

## 📁 Windows File Management

### Data Files Location

All your data files will be available in `C:\sewa\`:

```
C:\sewa\
├── All_Sent_Records.xlsx      # All sent message records
├── Duplicate_Transactions.xlsx # Duplicate transaction logs
├── Failed_Transactions.xlsx   # Failed transaction logs
├── config.env                 # Configuration file
├── data\                      # Application data
├── exports\                   # Validation results
│   ├── phone_validation\      # Phone validation results
│   ├── address_validation\    # Address validation results
│   └── duplicate_detection\   # Duplicate detection results
└── uploads\                   # Uploaded Excel files
```

### File Access

- **Direct Access**: Open files directly in Windows Explorer
- **Excel Integration**: Open Excel files directly in Microsoft Excel
- **Backup**: Copy files to backup location
- **Sharing**: Share files with other users

## 🐛 Windows Troubleshooting

### Container Won't Start

#### Check Docker Desktop:
1. **Ensure Docker Desktop is running**
2. **Check WSL 2 status**
3. **Verify file sharing is enabled**

#### Check Port Conflicts:
```cmd
# Check if port 8501 is in use
netstat -ano | findstr :8501

# Kill process if needed (replace PID)
taskkill /PID <PID> /F
```

#### Check Volume Mounts:
1. **Verify directories exist**: `C:\sewa\data`, `C:\sewa\exports`, etc.
2. **Check file permissions**
3. **Ensure Docker Desktop file sharing includes** `C:\sewa`

### Application Not Accessible

#### Check Container Status:
1. **Go to Containers tab**
2. **Verify container is "Running"**
3. **Check health status**

#### Check Port Mapping:
1. **Verify port mapping**: `8501:8501`
2. **Try different port**: `8502:8501`
3. **Access**: http://localhost:8502

#### Check Logs:
1. **View container logs** in Docker Desktop
2. **Look for startup errors**
3. **Check for API key issues**

### Performance Issues

#### Increase Resources:
1. **Docker Desktop Settings**
2. **Resources → Advanced**
3. **Increase Memory to 8GB**
4. **Increase CPUs to 4**
5. **Restart Docker Desktop**

#### Windows Optimization:
```powershell
# Add Windows Defender exclusions
Add-MpPreference -ExclusionPath "C:\sewa"
Add-MpPreference -ExclusionProcess "docker.exe"
```

## 🔄 Updates and Maintenance

### Update Application

1. **Stop the container**
2. **Update your code** in `C:\sewa`
3. **Rebuild the image** in Docker Desktop
4. **Run the new container**

### Backup Data

```cmd
# Create backup
powershell -Command "Compress-Archive -Path 'C:\sewa\All_Sent_Records.xlsx', 'C:\sewa\Duplicate_Transactions.xlsx', 'C:\sewa\Failed_Transactions.xlsx', 'C:\sewa\exports', 'C:\sewa\uploads' -DestinationPath 'C:\sewa\backup.zip'"
```

### Restore Data

```cmd
# Extract backup
powershell -Command "Expand-Archive -Path 'C:\sewa\backup.zip' -DestinationPath 'C:\sewa'"
```

## 🎯 Windows-Specific Benefits

### ✅ User-Friendly
- **Visual Interface**: Easy-to-use Docker Desktop GUI
- **Windows Integration**: Native Windows file access
- **No Command Line**: Point-and-click operations

### ✅ File Management
- **Direct Access**: Open files directly in Windows Explorer
- **Excel Integration**: Native Excel file support
- **Backup/Restore**: Easy Windows file operations

### ✅ Monitoring
- **Real-time Stats**: Live container monitoring
- **Log Viewing**: Easy log access and filtering
- **Health Monitoring**: Visual health status

### ✅ Performance
- **WSL 2 Backend**: Better performance than Hyper-V
- **Resource Control**: Easy resource allocation
- **Windows Optimization**: Native Windows performance

## 📋 Quick Reference

| Task | Docker Desktop GUI Action |
|------|---------------------------|
| Build Image | Images tab → Build → Configure → Build |
| Run Container | Containers tab → Run → Configure → Run |
| Start Container | Containers tab → Click Play ▶️ |
| Stop Container | Containers tab → Click Stop ⏹️ |
| View Logs | Containers tab → Click container → Logs tab |
| View Stats | Containers tab → Click container → Stats tab |
| Edit Settings | Containers tab → Click Settings ⚙️ |
| Access App | http://localhost:8501 |

## 🎉 Success Checklist

- [ ] Docker Desktop installed and running
- [ ] WSL 2 enabled and working
- [ ] Project files in `C:\sewa`
- [ ] Data directories created
- [ ] `config.env` configured with API keys
- [ ] Docker image built successfully
- [ ] Container running and healthy
- [ ] Application accessible at http://localhost:8501
- [ ] Data files persisting in `C:\sewa`

---

**🎉 Your SEWA Book Automation System is now ready to run on Windows using Docker Desktop GUI!**

## 📞 Support

If you encounter issues:
1. **Check Docker Desktop logs**
2. **View container logs** in Docker Desktop
3. **Verify Windows Defender exclusions**
4. **Check WSL 2 status**
5. **Ensure file sharing is enabled**

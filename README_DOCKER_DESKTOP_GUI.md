# 🐳 SEWA Book Automation System - Docker Desktop GUI

## 🎯 Quick Start

### 1. Prerequisites
- Docker Desktop installed and running
- Your API keys ready

### 2. Setup (Windows)
```cmd
# Run as Administrator
setup-docker-desktop.bat
```

### 3. Build Image
1. Open Docker Desktop
2. Go to Images tab
3. Click "Build" button
4. Configure:
   - Build context: Your project folder
   - Dockerfile: Dockerfile
   - Image name: sewa-book-automation
   - Tag: latest
5. Click "Build"

### 4. Run Container
1. Go to Containers tab
2. Click "Run" button
3. Select image: sewa-book-automation:latest
4. Configure settings (see template below)
5. Click "Run"

### 5. Access Application
- **URL**: http://localhost:8501
- **Data Files**: Available in your project directory

## 📋 Container Configuration Template

### Basic Settings
```
Container name: sewa-book-automation
Ports: 8501:8501
```

### Environment Variables
```
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
PYTHONUNBUFFERED=1
```

### Volume Mounts
```
./data:/app/data
./exports:/app/exports
./All_Sent_Records.xlsx:/app/All_Sent_Records.xlsx
./Duplicate_Transactions.xlsx:/app/Duplicate_Transactions.xlsx
./Failed_Transactions.xlsx:/app/Failed_Transactions.xlsx
./config.env:/app/config.env
./uploads:/app/uploads
```

### Advanced Settings
```
Restart policy: Unless stopped
Memory: 4GB
CPU: 4 cores
```

## 🛠️ Management

### Start/Stop Container
- **Start**: Containers tab → Click Play ▶️
- **Stop**: Containers tab → Click Stop ⏹️
- **Restart**: Containers tab → Click Restart 🔄

### View Logs
- Containers tab → Click container → Logs tab

### View Stats
- Containers tab → Click container → Stats tab

## 📁 Data Files

All data files are available in your project directory:
- `All_Sent_Records.xlsx` - All sent message records
- `Duplicate_Transactions.xlsx` - Duplicate transaction logs
- `Failed_Transactions.xlsx` - Failed transaction logs
- `exports/` - Validation results
- `uploads/` - Uploaded files

## 🔧 Troubleshooting

### Container Won't Start
1. Check Docker Desktop is running
2. Verify port 8501 is not in use
3. Check volume mount paths
4. View container logs

### Application Not Accessible
1. Check container is running
2. Verify port mapping 8501:8501
3. Check health status
4. View application logs

## 📖 Documentation

- **`DOCKER_DESKTOP_GUI_SETUP.md`** - Detailed setup guide
- **`WINDOWS_DOCKER_DESKTOP_GUI.md`** - Windows-specific guide
- **`DOCKER_DESKTOP_GUI_SUMMARY.md`** - Comprehensive summary
- **`docker-desktop-config-template.txt`** - Configuration template

## 🎉 Features

- ✅ **Twilio Phone Validation** - Real-time carrier information
- ✅ **VoIP/Landline Blocking** - Prevents sending to invalid numbers
- ✅ **Address Validation** - Google Maps geocoding
- ✅ **Duplicate Detection** - Prevents duplicate messages
- ✅ **SMS & WhatsApp** - Dual messaging capabilities
- ✅ **Comprehensive Analytics** - Book distribution, trends, quality metrics
- ✅ **Data Export** - Excel files with timestamps
- ✅ **Multithreading** - Fast parallel processing
- ✅ **Docker Desktop GUI** - User-friendly interface

---

**🚀 Your SEWA Book Automation System is ready to run with Docker Desktop GUI!**

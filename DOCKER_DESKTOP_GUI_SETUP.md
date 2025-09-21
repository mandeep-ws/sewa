# 🐳 Docker Desktop GUI Setup Guide

This guide explains how to run the SEWA Book Automation System using Docker Desktop's graphical interface instead of Docker Compose.

## 📋 Prerequisites

- Docker Desktop installed and running
- Your API keys and credentials configured

## 🚀 Setup Steps

### Step 1: Build the Docker Image

#### Option A: Using Docker Desktop GUI
1. **Open Docker Desktop**
2. **Go to Images tab**
3. **Click "Build" button**
4. **Configure build settings:**
   - **Build context**: Select your project folder (e.g., `C:\sewa`)
   - **Dockerfile**: `Dockerfile` (should be auto-detected)
   - **Image name**: `sewa-book-automation`
   - **Tag**: `latest`
5. **Click "Build"**

#### Option B: Using Command Line (One-time)
```bash
# Build the image
docker build -t sewa-book-automation:latest .
```

### Step 2: Create Container Configuration

#### Using Docker Desktop GUI:
1. **Go to Containers tab**
2. **Click "Run" button**
3. **Select your image**: `sewa-book-automation:latest`
4. **Configure container settings:**

#### Container Configuration:
- **Container name**: `sewa-book-automation`
- **Port mapping**: `8501:8501`
- **Environment variables**: (Add these)
  - `STREAMLIT_SERVER_PORT=8501`
  - `STREAMLIT_SERVER_ADDRESS=0.0.0.0`
  - `PYTHONUNBUFFERED=1`

#### Volume Mounts (Data Persistence):
Add these volume mounts to keep your data on the host machine:

| Host Path | Container Path | Description |
|-----------|----------------|-------------|
| `./data` | `/app/data` | Application data |
| `./exports` | `/app/exports` | Validation results |
| `./All_Sent_Records.xlsx` | `/app/All_Sent_Records.xlsx` | Sent records |
| `./Duplicate_Transactions.xlsx` | `/app/Duplicate_Transactions.xlsx` | Duplicate logs |
| `./Failed_Transactions.xlsx` | `/app/Failed_Transactions.xlsx` | Failed logs |
| `./config.env` | `/app/config.env` | Configuration file |
| `./uploads` | `/app/uploads` | Uploaded files |

### Step 3: Advanced Settings

#### Resource Limits:
- **Memory**: 2GB minimum (4GB recommended)
- **CPU**: 2 cores minimum (4 cores recommended)

#### Restart Policy:
- **Restart policy**: `Unless stopped`

#### Health Check:
- **Health check command**: `curl -f http://localhost:8501/_stcore/health || exit 1`
- **Interval**: 30s
- **Timeout**: 10s
- **Retries**: 3
- **Start period**: 40s

## 🎯 Step-by-Step GUI Instructions

### 1. Build Image in Docker Desktop

1. **Open Docker Desktop**
2. **Navigate to Images tab**
3. **Click "Build" button**
4. **Fill in the form:**
   ```
   Build context: [Browse to your project folder]
   Dockerfile: Dockerfile
   Image name: sewa-book-automation
   Tag: latest
   ```
5. **Click "Build"**
6. **Wait for build to complete**

### 2. Run Container in Docker Desktop

1. **Go to Containers tab**
2. **Click "Run" button**
3. **Select image**: `sewa-book-automation:latest`
4. **Configure the container:**

#### Basic Settings:
```
Container name: sewa-book-automation
Ports: 8501:8501
```

#### Environment Variables:
```
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
PYTHONUNBUFFERED=1
```

#### Volume Mounts:
```
./data:/app/data
./exports:/app/exports
./All_Sent_Records.xlsx:/app/All_Sent_Records.xlsx
./Duplicate_Transactions.xlsx:/app/Duplicate_Transactions.xlsx
./Failed_Transactions.xlsx:/app/Failed_Transactions.xlsx
./config.env:/app/config.env
./uploads:/app/uploads
```

#### Advanced Settings:
```
Restart policy: Unless stopped
Memory: 4GB
CPU: 4 cores
```

5. **Click "Run"**

### 3. Access the Application

1. **Wait for container to start** (check status in Containers tab)
2. **Open your browser**
3. **Navigate to**: http://localhost:8501
4. **The SEWA Book Automation System should load**

## 📁 Data Persistence Setup

### Create Required Directories

Before running the container, create these directories on your host machine:

```bash
# Windows (Command Prompt)
mkdir data
mkdir exports
mkdir exports\phone_validation
mkdir exports\address_validation
mkdir exports\duplicate_detection
mkdir uploads

# Windows (PowerShell)
New-Item -ItemType Directory -Path "data", "exports", "exports\phone_validation", "exports\address_validation", "exports\duplicate_detection", "uploads" -Force

# Linux/Mac
mkdir -p data exports/phone_validation exports/address_validation exports/duplicate_detection uploads
```

### Create Initial Files

```bash
# Create empty Excel files
touch All_Sent_Records.xlsx
touch Duplicate_Transactions.xlsx
touch Failed_Transactions.xlsx

# Create config.env template
echo "TWILIO_ACCOUNT_SID=your_account_sid_here" > config.env
echo "TWILIO_AUTH_TOKEN=your_auth_token_here" >> config.env
echo "TWILIO_SMS_PHONE_NUMBER=+1234567890" >> config.env
echo "TWILIO_WHATSAPP_PHONE_NUMBER=+1234567890" >> config.env
echo "GOOGLE_MAPS_API_KEY=your_google_maps_api_key" >> config.env
echo "ABSTRACT_API_KEY=your_abstract_api_key_here" >> config.env
```

## 🔧 Container Management

### Using Docker Desktop GUI

#### Start Container:
1. **Go to Containers tab**
2. **Find your container**: `sewa-book-automation`
3. **Click the "Play" button**

#### Stop Container:
1. **Go to Containers tab**
2. **Find your container**: `sewa-book-automation`
3. **Click the "Stop" button**

#### Restart Container:
1. **Go to Containers tab**
2. **Find your container**: `sewa-book-automation`
3. **Click the "Restart" button**

#### View Logs:
1. **Go to Containers tab**
2. **Find your container**: `sewa-book-automation`
3. **Click on the container name**
4. **Go to "Logs" tab**

#### Edit Container:
1. **Go to Containers tab**
2. **Find your container**: `sewa-book-automation`
3. **Click the "Settings" button**
4. **Modify settings as needed**
5. **Click "Save"**

### Using Command Line (Alternative)

```bash
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

## 🐛 Troubleshooting

### Container Won't Start

1. **Check logs in Docker Desktop**:
   - Go to Containers tab
   - Click on your container
   - View logs for error messages

2. **Check port conflicts**:
   - Ensure port 8501 is not in use
   - Change port mapping if needed (e.g., 8502:8501)

3. **Check volume mounts**:
   - Ensure all directories exist on host
   - Check file permissions

### Application Not Accessible

1. **Check container status**:
   - Container should be "Running"
   - Health check should be "Healthy"

2. **Check port mapping**:
   - Verify 8501:8501 mapping is correct
   - Try accessing http://localhost:8501

3. **Check logs**:
   - Look for startup errors
   - Check for API key issues

### Data Not Persisting

1. **Check volume mounts**:
   - Verify all volumes are properly mounted
   - Check host directory permissions

2. **Check file permissions**:
   - Ensure container can write to mounted directories
   - Check file ownership

## 📊 Monitoring

### Container Stats

1. **Go to Containers tab**
2. **Click on your container**
3. **View "Stats" tab** for:
   - CPU usage
   - Memory usage
   - Network I/O
   - Disk I/O

### Health Monitoring

1. **Check health status** in Containers tab
2. **View health check logs** if issues occur
3. **Monitor application logs** for errors

## 🔄 Updates

### Update Application

1. **Stop the container**
2. **Remove the old container** (optional)
3. **Rebuild the image** with latest code
4. **Run the new container** with same settings

### Backup Data

1. **Stop the container**
2. **Copy data files** from host directories
3. **Create backup archive**

## 🎯 Benefits of Docker Desktop GUI

### ✅ User-Friendly
- **Visual Interface**: Easy to use graphical interface
- **No Command Line**: No need to remember Docker commands
- **Point and Click**: Simple mouse operations

### ✅ Monitoring
- **Real-time Stats**: Live container statistics
- **Log Viewing**: Easy log access and filtering
- **Health Monitoring**: Visual health status

### ✅ Management
- **Container Control**: Start, stop, restart with clicks
- **Settings Management**: Easy configuration changes
- **Resource Monitoring**: Visual resource usage

### ✅ Debugging
- **Log Access**: Easy log viewing and filtering
- **Container Inspection**: Detailed container information
- **Network Monitoring**: Network connectivity status

## 📋 Quick Reference

| Task | Docker Desktop GUI Action |
|------|---------------------------|
| Build Image | Images tab → Build → Configure → Build |
| Run Container | Containers tab → Run → Configure → Run |
| Start Container | Containers tab → Click Play button |
| Stop Container | Containers tab → Click Stop button |
| View Logs | Containers tab → Click container → Logs tab |
| View Stats | Containers tab → Click container → Stats tab |
| Edit Settings | Containers tab → Click Settings button |

---

**🎉 Your SEWA Book Automation System is now ready to run using Docker Desktop GUI!**

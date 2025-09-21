# 🐳 Docker Deployment Guide

This guide explains how to run the SEWA Book Automation System using Docker Desktop.

## 📋 Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)
- Your API keys and credentials

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Run the setup script
./setup-docker.sh
```

### 2. Configure API Keys

Create or edit `config.env` with your credentials:

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

### 3. Build and Run

```bash
# Build and start the application
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access Application

Open your browser and go to: **http://localhost:8501**

## 📁 Data Persistence

All important files are mounted to your host machine:

### Data Files (Available on Host)
- `./All_Sent_Records.xlsx` - All sent message records
- `./Duplicate_Transactions.xlsx` - Duplicate transaction logs
- `./Failed_Transactions.xlsx` - Failed transaction logs
- `./config.env` - Configuration file

### Export Directories (Available on Host)
- `./exports/phone_validation/` - Phone validation results
- `./exports/address_validation/` - Address validation results
- `./exports/duplicate_detection/` - Duplicate detection results

### Upload Directory (Available on Host)
- `./uploads/` - Uploaded Excel files

## 🛠️ Docker Commands

### Basic Operations
```bash
# Start the application
docker-compose up -d

# Stop the application
docker-compose down

# View logs
docker-compose logs -f

# Restart the application
docker-compose restart

# Rebuild and start
docker-compose up -d --build
```

### Development Commands
```bash
# Build without cache
docker-compose build --no-cache

# View container status
docker-compose ps

# Execute commands in container
docker-compose exec sewa-app bash

# View container logs
docker-compose logs sewa-app
```

## 🔧 Configuration

### Environment Variables
The application uses the following environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | Yes |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | Yes |
| `TWILIO_SMS_PHONE_NUMBER` | Twilio SMS Phone Number | Yes |
| `TWILIO_WHATSAPP_PHONE_NUMBER` | Twilio WhatsApp Phone Number | Yes |
| `GOOGLE_MAPS_API_KEY` | Google Maps API Key | Yes |
| `ABSTRACT_API_KEY` | Abstract API Key (Optional) | No |

### Port Configuration
- **Application Port**: 8501 (Streamlit default)
- **Host Access**: http://localhost:8501

## 📊 Monitoring

### Health Check
The container includes a health check that monitors the application:
- **Check Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3 attempts
- **Start Period**: 40 seconds

### Logs
View application logs:
```bash
# Follow logs in real-time
docker-compose logs -f sewa-app

# View last 100 lines
docker-compose logs --tail=100 sewa-app
```

## 🔒 Security

### Non-Root User
The application runs as a non-root user (`appuser`) for security.

### File Permissions
All data directories are created with proper permissions (755).

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using port 8501
lsof -i :8501

# Kill the process or change port in docker-compose.yml
```

#### 2. Permission Issues
```bash
# Fix permissions
sudo chown -R $USER:$USER ./data ./exports ./uploads
chmod -R 755 ./data ./exports ./uploads
```

#### 3. Container Won't Start
```bash
# Check logs
docker-compose logs sewa-app

# Rebuild container
docker-compose down
docker-compose up -d --build
```

#### 4. API Key Issues
- Verify `config.env` exists and has correct values
- Check that API keys are valid and have proper permissions
- Ensure no extra spaces or quotes in the config file

### Debug Mode
```bash
# Run in debug mode with shell access
docker-compose run --rm sewa-app bash

# Check environment variables
docker-compose exec sewa-app env | grep TWILIO
```

## 📈 Performance

### Resource Usage
- **Memory**: ~200-500MB (depending on data size)
- **CPU**: Low usage (mostly I/O bound)
- **Storage**: Minimal (data stored on host)

### Optimization Tips
1. Use SSD storage for better I/O performance
2. Allocate at least 2GB RAM to Docker Desktop
3. Enable file sharing for the project directory

## 🔄 Updates

### Updating the Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Backup Data
```bash
# Backup all data files
tar -czf sewa-backup-$(date +%Y%m%d).tar.gz \
  All_Sent_Records.xlsx \
  Duplicate_Transactions.xlsx \
  Failed_Transactions.xlsx \
  exports/ \
  uploads/
```

## 📞 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f sewa-app`
2. Verify your `config.env` file
3. Ensure Docker Desktop is running
4. Check that all required ports are available

## 🎯 Features Available in Docker

✅ **Phone Validation** - Twilio Lookup API integration  
✅ **Address Validation** - Google Maps Geocoding API  
✅ **Duplicate Detection** - Historical record matching  
✅ **Message Sending** - SMS and WhatsApp via Twilio  
✅ **Data Export** - Excel files with timestamps  
✅ **Analytics Dashboard** - Comprehensive reporting  
✅ **VoIP Blocking** - Automatic VoIP/landline detection  
✅ **Multithreading** - Parallel processing for performance  

---

**🎉 Your SEWA Book Automation System is now ready to run in Docker!**

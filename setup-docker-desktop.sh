#!/bin/bash

echo "========================================"
echo "  SEWA Book Automation System Setup"
echo "  Docker Desktop GUI Configuration"
echo "========================================"
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    echo "Please install Docker Desktop first"
    exit 1
fi

echo "✅ Docker is installed"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo "✅ Docker is running"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data
mkdir -p exports/phone_validation
mkdir -p exports/address_validation
mkdir -p exports/duplicate_detection
mkdir -p uploads

# Create initial files if they don't exist
echo "📄 Creating initial files..."
touch All_Sent_Records.xlsx
touch Duplicate_Transactions.xlsx
touch Failed_Transactions.xlsx

# Check if config.env exists
if [ ! -f "config.env" ]; then
    echo "⚠️  config.env file not found!"
    echo "Creating template config.env file..."
    cat > config.env << EOF
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_SMS_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_PHONE_NUMBER=+1234567890

# Google Maps API
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Enhanced Phone Validation (Optional)
ABSTRACT_API_KEY=your_abstract_api_key_here
EOF
    echo "✅ Template config.env created"
else
    echo "✅ config.env file exists"
fi

# Build Docker image
echo "🔨 Building Docker image..."
echo "This may take 5-10 minutes..."
docker build -t sewa-book-automation:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
else
    echo "❌ Docker image build failed"
    exit 1
fi

echo
echo "✅ Setup completed successfully!"
echo
echo "🎯 Next Steps:"
echo
echo "1. Open Docker Desktop"
echo "2. Go to Containers tab"
echo "3. Click 'Run' button"
echo "4. Select image: sewa-book-automation:latest"
echo "5. Configure container settings (see docker-desktop-config.txt)"
echo "6. Click 'Run'"
echo "7. Access application at: http://localhost:8501"
echo
echo "📖 Configuration template available in: docker-desktop-config.txt"
echo
echo "🎉 Your SEWA Book Automation System is ready!"

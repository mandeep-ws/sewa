#!/bin/bash

# Setup script for Docker deployment
echo "🐳 Setting up SEWA Book Automation System for Docker..."

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

# Set proper permissions
echo "🔐 Setting permissions..."
chmod 755 data
chmod 755 exports
chmod 755 exports/phone_validation
chmod 755 exports/address_validation
chmod 755 exports/duplicate_detection
chmod 755 uploads

# Check if config.env exists
if [ ! -f "config.env" ]; then
    echo "⚠️  Warning: config.env file not found!"
    echo "Please create config.env with your API keys and Twilio credentials."
    echo "Example config.env content:"
    echo ""
    echo "TWILIO_ACCOUNT_SID=your_account_sid_here"
    echo "TWILIO_AUTH_TOKEN=your_auth_token_here"
    echo "TWILIO_SMS_PHONE_NUMBER=your_sms_phone_number"
    echo "TWILIO_WHATSAPP_PHONE_NUMBER=your_whatsapp_phone_number"
    echo "GOOGLE_MAPS_API_KEY=your_google_maps_api_key"
    echo "ABSTRACT_API_KEY=your_abstract_api_key_here"
    echo ""
fi

echo "✅ Setup completed!"
echo ""
echo "🚀 To run the application:"
echo "   docker-compose up -d"
echo ""
echo "🌐 Access the application at:"
echo "   http://localhost:8501"
echo ""
echo "📁 Data files will be available in:"
echo "   ./data/ - Application data"
echo "   ./exports/ - Validation results"
echo "   ./uploads/ - Uploaded files"
echo "   ./All_Sent_Records.xlsx - Sent records"
echo "   ./Duplicate_Transactions.xlsx - Duplicate transactions"
echo "   ./Failed_Transactions.xlsx - Failed transactions"
echo ""
echo "🛑 To stop the application:"
echo "   docker-compose down"

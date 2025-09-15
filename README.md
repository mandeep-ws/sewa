# 📚 Book Request Automation System

A comprehensive web application for automating the book request process, including data validation, duplicate detection, and automated messaging via WhatsApp and SMS.

## 🚀 Features

- **📁 File Upload**: Upload weekly SMS.xlsx files
- **📞 Phone Validation**: Validate phone numbers with carrier information
- **🏠 Address Validation**: Google Geocoding integration for address verification
- **🔄 Duplicate Detection**: Find existing customers in your Book.xlsx database
- **📱 Message Automation**: Send WhatsApp and SMS messages automatically
- **📊 Analytics**: Comprehensive reporting and data visualization
- **✅ User Confirmation**: Review and confirm messages before sending

## 🛠️ Installation

### Prerequisites

- Python 3.10 or higher
- Google Maps API key (for address validation)
- Twilio account (for SMS/WhatsApp messaging)

### Setup

1. **Clone or download the project**
   ```bash
   cd /path/to/sewa
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   ```

3. **Configure environment variables**
   ```bash
   cp config.env.example .env
   ```
   
   Edit `.env` file with your API keys:
   ```
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
   TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
   TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
   TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

   Or directly with Streamlit:
   ```bash
   streamlit run app.py
   ```

## 📋 Usage

### 1. Upload Data
- Navigate to the "📁 Upload Data" tab
- Upload your weekly SMS.xlsx file
- Review the data preview and quality metrics

### 2. Validate Data
- Go to "🔍 Validate Data" tab
- Click "📞 Validate Phone Numbers" to check phone numbers and get carrier info
- Click "🏠 Validate Addresses" to verify addresses using Google Geocoding
- Click "🔄 Check Duplicates" to find existing customers

### 3. Send Messages
- Navigate to "📱 Send Messages" tab
- Review pending messages and duplicates
- Choose to send WhatsApp only, SMS only, or both
- Confirm and send messages

### 4. View Analytics
- Check "📊 Analytics" tab for insights
- View book distribution, language preferences, and geographic data
- Monitor data quality metrics

## 🔧 Configuration

### Google Maps API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Geocoding API
3. Create an API key
4. Add the key to your `.env` file

### Twilio Setup
1. Sign up for [Twilio](https://www.twilio.com/)
2. Get your Account SID and Auth Token
3. Purchase a phone number
4. Add credentials to your `.env` file

## 📁 File Structure

```
sewa/
├── app.py                 # Main Streamlit application
├── main.py               # Application entry point
├── modules/              # Core functionality modules
│   ├── data_processor.py    # Data loading and processing
│   ├── phone_validator.py   # Phone number validation
│   ├── address_validator.py # Address validation with Google Maps
│   ├── duplicate_detector.py # Duplicate customer detection
│   ├── message_sender.py    # WhatsApp/SMS sending
│   └── ui_components.py     # UI components and displays
├── Book.xlsx            # Your existing book database
├── Sms.xlsx             # Weekly SMS data (uploaded)
├── config.env.example   # Environment variables template
└── README.md           # This file
```

## 🎯 Workflow

The system automates your manual process:

1. **Data Collection**: Import from SMS.xlsx
2. **Data Processing**: Clean and standardize addresses/phones
3. **Validation**: Verify phone numbers and addresses
4. **Duplicate Detection**: Check against Book.xlsx history
5. **Message Generation**: Create appropriate messages based on customer status
6. **Communication**: Send via WhatsApp/SMS with fallback options
7. **Tracking**: Monitor delivery status and update records

## 📊 Message Types

The system automatically selects the right message template:

- **Column X**: For new customers without book/language info
- **Column Y**: For new customers with complete book/language info  
- **Column Z**: For repeat customers (duplicates)

## 🔒 Security

- API keys are stored in environment variables
- No sensitive data is logged or stored
- All communications are encrypted via Twilio

## 🐛 Troubleshooting

### Common Issues

1. **"Google Maps API not configured"**
   - Check your API key in `.env` file
   - Ensure Geocoding API is enabled

2. **"Twilio not configured"**
   - Verify Twilio credentials in `.env` file
   - Check phone number format

3. **"Module not found"**
   - Run `pip install -e .` to install dependencies

### Support

For issues or questions, check the application logs or contact support.

## 📈 Performance

- **Phone Validation**: ~0.1s per number
- **Address Validation**: ~0.2s per address (Google API rate limits)
- **Duplicate Detection**: ~0.01s per record
- **Message Sending**: ~1-2s per message (Twilio rate limits)

## 🔄 Updates

The system is designed to be easily extensible. New features can be added by:

1. Adding new modules in the `modules/` directory
2. Updating the main `app.py` file
3. Adding new UI components in `ui_components.py`

---

**Built with ❤️ for automating book request processes**

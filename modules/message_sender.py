"""
Message sending module for WhatsApp and SMS
"""

import pandas as pd
import streamlit as st
import requests
import time
from twilio.rest import Client
import os
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from config.env
load_dotenv('config.env')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('message_sending.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MessageSender:
    def __init__(self):
        logger.info("🔧 Initializing MessageSender...")
        
        # Initialize Twilio client for SMS
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        logger.info(f"📋 Twilio Account SID: {self.twilio_account_sid[:10]}..." if self.twilio_account_sid else "❌ No Account SID")
        logger.info(f"🔑 Twilio Auth Token: {'***' + self.twilio_auth_token[-4:] if self.twilio_auth_token else '❌ No Auth Token'}")
        logger.info(f"📞 Twilio Phone Number: {self.twilio_phone_number if self.twilio_phone_number else '❌ No Phone Number'}")
        
        if self.twilio_account_sid and self.twilio_auth_token:
            try:
                self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
                logger.info("✅ Twilio client initialized successfully")
                
                # Test the connection
                try:
                    account = self.twilio_client.api.accounts(self.twilio_account_sid).fetch()
                    logger.info(f"✅ Twilio connection test successful - Account: {account.friendly_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Twilio connection test failed: {str(e)}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to initialize Twilio client: {str(e)}")
                self.twilio_client = None
        else:
            self.twilio_client = None
            logger.error("❌ Twilio credentials not found. SMS sending will be disabled.")
            st.warning("⚠️ Twilio credentials not found. SMS sending will be disabled.")
    
    def send_whatsapp_message(self, phone_number, message):
        """Send WhatsApp message using Twilio"""
        logger.info(f"💬 Starting WhatsApp send to: {phone_number}")
        logger.info(f"📝 Message: {message[:50]}...")
        
        if not self.twilio_client:
            error_msg = 'Twilio not configured'
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
        
        try:
            # Validate and format phone number properly
            logger.info(f"🔍 Validating phone number: {phone_number}")
            is_valid, formatted_number = self.validate_phone_for_sending(phone_number)
            if not is_valid:
                error_msg = f"Phone validation failed: {formatted_number}"
                logger.error(f"❌ {error_msg}")
                return {'success': False, 'error': error_msg}
            
            logger.info(f"✅ Phone validation passed: {formatted_number}")
            
            # Format phone number for WhatsApp
            whatsapp_number = f"whatsapp:+{formatted_number}"
            logger.info(f"📞 WhatsApp number: {whatsapp_number}")
            logger.info(f"📞 Sending from: whatsapp:{self.twilio_phone_number}")
            
            # Send message
            logger.info("🚀 Sending WhatsApp via Twilio...")
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=f"whatsapp:{self.twilio_phone_number}",
                to=whatsapp_number
            )
            
            logger.info(f"✅ WhatsApp sent successfully!")
            logger.info(f"📋 Message SID: {message_obj.sid}")
            logger.info(f"📊 Status: {message_obj.status}")
            logger.info(f"💰 Price: {getattr(message_obj, 'price', 'N/A')}")
            
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'status': message_obj.status,
                'error': None
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ WhatsApp sending failed: {error_msg}")
            logger.error(f"📞 Phone: {phone_number}")
            logger.error(f"📝 Message: {message[:100]}...")
            return {
                'success': False,
                'error': error_msg,
                'message_sid': None,
                'status': 'failed'
            }
    
    def send_sms_message(self, phone_number, message):
        """Send SMS message using Twilio"""
        logger.info(f"📱 Starting SMS send to: {phone_number}")
        logger.info(f"📝 Message: {message[:50]}...")
        
        if not self.twilio_client:
            error_msg = 'Twilio not configured'
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
        
        try:
            # Validate and format phone number properly
            logger.info(f"🔍 Validating phone number: {phone_number}")
            is_valid, formatted_number = self.validate_phone_for_sending(phone_number)
            if not is_valid:
                error_msg = f"Phone validation failed: {formatted_number}"
                logger.error(f"❌ {error_msg}")
                return {'success': False, 'error': error_msg}
            
            logger.info(f"✅ Phone validation passed: {formatted_number}")
            
            # Add + prefix for international format
            formatted_number = f"+{formatted_number}"
            logger.info(f"📞 Formatted phone number: {formatted_number}")
            logger.info(f"📞 Sending from: {self.twilio_phone_number}")
            
            # Send message
            logger.info("🚀 Sending SMS via Twilio...")
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=formatted_number
            )
            
            logger.info(f"✅ SMS sent successfully!")
            logger.info(f"📋 Message SID: {message_obj.sid}")
            logger.info(f"📊 Status: {message_obj.status}")
            logger.info(f"💰 Price: {getattr(message_obj, 'price', 'N/A')}")
            
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'status': message_obj.status,
                'error': None
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ SMS sending failed: {error_msg}")
            logger.error(f"📞 Phone: {phone_number}")
            logger.error(f"📝 Message: {message[:100]}...")
            return {
                'success': False,
                'error': error_msg,
                'message_sid': None,
                'status': 'failed'
            }
    
    def send_both_messages(self, phone_number, message):
        """Send both WhatsApp and SMS messages"""
        results = {
            'whatsapp': self.send_whatsapp_message(phone_number, message),
            'sms': self.send_sms_message(phone_number, message)
        }
        
        # Determine overall success
        whatsapp_success = results['whatsapp']['success']
        sms_success = results['sms']['success']
        
        if whatsapp_success or sms_success:
            results['overall_success'] = True
            results['status'] = 'partial' if not (whatsapp_success and sms_success) else 'complete'
        else:
            results['overall_success'] = False
            results['status'] = 'failed'
        
        return results
    
    def batch_send_whatsapp(self, recipients_data):
        """Send WhatsApp messages to multiple recipients"""
        results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, recipient in enumerate(recipients_data):
            progress = (idx + 1) / len(recipients_data)
            progress_bar.progress(progress)
            status_text.text(f"Sending WhatsApp to {recipient['name']} ({idx + 1}/{len(recipients_data)})")
            
            result = self.send_whatsapp_message(
                recipient['phone'],
                recipient['message']
            )
            
            result.update({
                'name': recipient['name'],
                'phone': recipient['phone'],
                'type': 'whatsapp'
            })
            
            results.append(result)
            
            # Add delay to respect rate limits
            time.sleep(1)
        
        progress_bar.progress(1.0)
        status_text.text("WhatsApp sending complete!")
        
        return results
    
    def batch_send_sms(self, recipients_data):
        """Send SMS messages to multiple recipients"""
        results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, recipient in enumerate(recipients_data):
            progress = (idx + 1) / len(recipients_data)
            progress_bar.progress(progress)
            status_text.text(f"Sending SMS to {recipient['name']} ({idx + 1}/{len(recipients_data)})")
            
            result = self.send_sms_message(
                recipient['phone'],
                recipient['message']
            )
            
            result.update({
                'name': recipient['name'],
                'phone': recipient['phone'],
                'type': 'sms'
            })
            
            results.append(result)
            
            # Add delay to respect rate limits
            time.sleep(1)
        
        progress_bar.progress(1.0)
        status_text.text("SMS sending complete!")
        
        return results
    
    def batch_send_both(self, recipients_data):
        """Send both WhatsApp and SMS to multiple recipients"""
        results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, recipient in enumerate(recipients_data):
            progress = (idx + 1) / len(recipients_data)
            progress_bar.progress(progress)
            status_text.text(f"Sending messages to {recipient['name']} ({idx + 1}/{len(recipients_data)})")
            
            result = self.send_both_messages(
                recipient['phone'],
                recipient['message']
            )
            
            result.update({
                'name': recipient['name'],
                'phone': recipient['phone'],
                'type': 'both'
            })
            
            results.append(result)
            
            # Add delay to respect rate limits
            time.sleep(2)  # Longer delay for both messages
        
        progress_bar.progress(1.0)
        status_text.text("Message sending complete!")
        
        return results
    
    def generate_whatsapp_link(self, phone_number, message):
        """Generate WhatsApp web link"""
        # URL encode the message
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        
        # Generate WhatsApp web link
        whatsapp_link = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"
        
        return whatsapp_link
    
    def get_message_status(self, message_sid):
        """Get the status of a sent message"""
        if not self.twilio_client:
            return None
        
        try:
            message = self.twilio_client.messages(message_sid).fetch()
            return {
                'status': message.status,
                'date_created': message.date_created,
                'date_sent': message.date_sent,
                'error_code': message.error_code,
                'error_message': message.error_message
            }
        except Exception as e:
            return {'error': str(e)}
    
    def format_phone_for_display(self, phone_number):
        """Format phone number for display"""
        if len(phone_number) == 11 and phone_number.startswith('1'):
            # Format as (XXX) XXX-XXXX
            return f"({phone_number[1:4]}) {phone_number[4:7]}-{phone_number[7:]}"
        return phone_number
    
    def validate_phone_for_sending(self, phone_number):
        """Validate phone number before sending"""
        if not phone_number:
            return False, "No phone number provided"
        
        # Remove non-digits
        import re
        clean_phone = re.sub(r'[^\d]', '', str(phone_number))
        
        # Check length
        if len(clean_phone) == 10:
            clean_phone = '1' + clean_phone
        elif len(clean_phone) == 11 and clean_phone.startswith('1'):
            pass
        else:
            return False, f"Invalid phone number format: {phone_number}"
        
        return True, clean_phone
    
    def get_duplicate_message_template(self, duplicate_record):
        """Get the appropriate message template for duplicate customers"""
        # This corresponds to the duplicate message template
        phone_matches = duplicate_record.get('phone_matches', [])
        address_matches = duplicate_record.get('address_matches', [])
        
        # Get the most recent match
        all_matches = phone_matches + address_matches
        if not all_matches:
            return None
        
        # Sort by date if available
        most_recent_match = all_matches[0]
        historical_record = most_recent_match.get('historical_data', {})
        
        # Get book name and language from current SMS request
        current_book_code = duplicate_record.get('sms_book', '')
        current_language = duplicate_record.get('sms_language', '')
        
        # Get previous book from historical record
        previous_book_code = historical_record.get('Book', '')
        previous_language = historical_record.get('Language', '')
        
        # Map book code to full name
        book_names = {
            'GG': 'Gyaan Ganga',
            'GTGA': 'Gita Tera Gyan Amrit',
            'JKR': 'Jeene ki Rah',
            'YBB': 'Yatharth Bhakti Bodh',
            'BSBT': 'Bhakti se bhagwan tak',
            'KP': 'Kabir parichay',
            'GGK': 'Garima Gitya ki',
            'HDM': 'Hindu Dharma Mahaan'
        }
        
        current_book_name = book_names.get(current_book_code, current_book_code)
        previous_book_name = book_names.get(previous_book_code, previous_book_code)
        
        # Check if it's the same book or different book
        if current_book_code == previous_book_code:
            # Same book - use original duplicate message
            message = f"""Hello, you requested a free book called *{current_book_name}* in {current_language} from Sant Rampal Ji Maharaj.

However our records indicate that we had already mailed you a free book in the past. Can you please confirm if you already received a book in the past?"""
        else:
            # Different book - ask if previous book was read and confirm new book
            message = f"""Hello, you requested a free book called *{current_book_name}* in {current_language} from Sant Rampal Ji Maharaj.

Our records show that we previously sent you a free book called *{previous_book_name}* in {previous_language}. 

Have you read the *{previous_book_name}*? Please confirm if you would like us to send the new book *{current_book_name}*."""
        
        return message
    
    def get_new_customer_message_template(self, sms_record, has_book_language=True):
        """Get message template for new customers"""
        name = sms_record.get('Name', '')
        address = sms_record.get('Address', '')
        book_code = sms_record.get('Book', '')
        language = sms_record.get('Language', '')
        
        # Map book code to full name
        book_names = {
            'GG': 'Gyaan Ganga',
            'GTGA': 'Gita Tera Gyan Amrit',
            'JKR': 'Jeene ki Rah',
            'YBB': 'Yatharth Bhakti Bodh',
            'BSBT': 'Bhakti se bhagwan tak',
            'KP': 'Kabir parichay',
            'GGK': 'Garima Gitya ki',
            'HDM': 'Hindu Dharma Mahaan'
        }
        
        book_name = book_names.get(book_code, book_code)
        
        if has_book_language and book_name and language:
            # Column Y - Confirm address and book request
            message = f"""Hello, you requested a free book called *{book_name}* in {language} from Sant Rampal Ji Maharaj.

Can you please confirm / provide the address to ensure it's not incorrect and has the full details (apartment or suite number) to be able to mail it:

{name}
{address}"""
        else:
            # Column X - Ask for language and confirm address
            message = f"""Hello, you requested a free book called *{book_name}* from Sant Rampal Ji Maharaj. Can you please let me know what language did you request it in (Hindi, English, Punjabi, Gujrati, other?).

Can you please confirm / provide the address to ensure it's not incorrect and has the full details to be able to mail it:

{name}
{address}"""
        
        return message

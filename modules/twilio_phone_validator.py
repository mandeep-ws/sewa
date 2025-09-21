"""
Twilio-based phone validation module with comprehensive carrier and line type detection
Uses Twilio Lookup API for accurate phone type detection to prevent sending to VoIP/landline
"""

import pandas as pd
import streamlit as st
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import requests
import time
import json
import os
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from modules.logger_config import get_logger
import concurrent.futures
import threading

# Load environment variables
load_dotenv('config.env')

logger = get_logger()

class TwilioPhoneValidator:
    def __init__(self):
        self.carrier_cache = {}
        self.twilio_client = None
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        
        # Initialize Twilio client if credentials are available
        if self.twilio_account_sid and self.twilio_auth_token:
            try:
                from twilio.rest import Client
                self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
                logger.info("✅ Twilio client initialized for Lookup API")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Twilio client: {e}")
        else:
            logger.warning("⚠️ Twilio credentials not found. Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in config.env")
        
        # Note: We rely entirely on Twilio Lookup API for carrier and line type detection
        # No need for manual VoIP carrier lists or patterns since Twilio provides this data directly
    
    def validate_phones(self, df, progress_callback=None, use_multithreading=True, max_workers=5):
        """
        Validate phone numbers using Twilio Lookup API with comprehensive carrier detection
        """
        total_phones = len(df[df['Phone'].notna() & (df['Phone'] != '')])
        results = []
        
        if use_multithreading and total_phones > 1:
            logger.info(f"Starting multithreaded Twilio phone validation for {total_phones} phones with {max_workers} workers.")
            processed_count = 0
            progress_lock = threading.Lock()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_phone = {executor.submit(self._process_single_phone, row['Phone'], idx): idx for idx, row in df.iterrows()}
                
                for future in concurrent.futures.as_completed(future_to_phone):
                    result = future.result()
                    results.append(result)
                    
                    with progress_lock:
                        processed_count += 1
                        if progress_callback:
                            progress_callback(processed_count, total_phones)
        else:
            logger.info(f"Starting sequential Twilio phone validation for {total_phones} phones.")
            for idx, row in df.iterrows():
                result = self._process_single_phone(row['Phone'], idx)
                results.append(result)
                if progress_callback:
                    progress_callback(idx + 1, total_phones)
                time.sleep(0.2)  # Rate limiting for Twilio API
        
        return pd.DataFrame(results)
    
    def _process_single_phone(self, phone_number_str, index):
        """Process a single phone number using Twilio Lookup API"""
        result = {
            'index': index,
            'original_phone': phone_number_str,
            'formatted_phone': phone_number_str,
            'is_valid': False,
            'carrier': 'Unknown',
            'carrier_type': 'Unknown',
            'line_type': 'Unknown',
            'is_mobile': False,
            'is_landline': False,
            'is_voip': False,
            'is_toll_free': False,
            'location': 'Unknown',
            'country': 'Unknown',
            'timezone': 'Unknown',
            'confidence': '0%',
            'detection_method': 'None',
            'error': None,
            'can_receive_sms': False,
            'can_receive_whatsapp': False
        }
        
        if not phone_number_str or str(phone_number_str).strip() == 'nan':
            result['error'] = 'Empty phone number'
            return result
        
        try:
            # First, validate with phonenumbers library
            parsed_number = phonenumbers.parse(phone_number_str, "US")
            if not phonenumbers.is_valid_number(parsed_number):
                result['error'] = 'Invalid phone number format (phonenumbers)'
                return result
            
            result['formatted_phone'] = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            
            # Try Twilio Lookup API first (most accurate)
            twilio_info = self._get_twilio_lookup_info(phone_number_str)
            if twilio_info:
                result.update(twilio_info)
                result['confidence'] = '95%'
                result['detection_method'] = 'Twilio Lookup API'
                result['is_valid'] = True
                
                # Determine if can receive SMS/WhatsApp
                result['can_receive_sms'] = result['is_mobile'] and not result['is_voip']
                result['can_receive_whatsapp'] = result['is_mobile'] and not result['is_voip']
                
                return result
            
            # Fallback to enhanced phonenumbers analysis
            phonenumbers_info = self._get_enhanced_phonenumbers_info(parsed_number)
            result.update(phonenumbers_info)
            result['confidence'] = '70%'
            result['detection_method'] = 'Enhanced phonenumbers'
            result['is_valid'] = True
            
            # Determine if can receive SMS/WhatsApp
            result['can_receive_sms'] = result['is_mobile'] and not result['is_voip']
            result['can_receive_whatsapp'] = result['is_mobile'] and not result['is_voip']
            
            return result
            
        except Exception as e:
            result['error'] = f'Processing error: {str(e)}'
            logger.error(f"Error processing phone {phone_number_str}: {e}")
            return result
    
    def _get_twilio_lookup_info(self, phone_number):
        """Get comprehensive phone information from Twilio Lookup API"""
        if not self.twilio_client:
            return None
        
        try:
            # Use Twilio Lookup API v1 with carrier type (as shown in your sample)
            try:
                # Use the v1 API with Type=carrier parameter
                phone_number_object = self.twilio_client.lookups.v1.phone_numbers(phone_number).fetch(
                    type='carrier'
                )
            except Exception as e:
                logger.warning(f"Twilio Lookup API v1 error: {e}")
                # If v1 fails, return None to fall back to phonenumbers
                return None
            
            result = {
                'is_valid': True,
                'carrier': 'Unknown',
                'carrier_type': 'Unknown',
                'line_type': 'Unknown',
                'is_mobile': False,
                'is_landline': False,
                'is_voip': False,
                'is_toll_free': False,
                'location': 'Unknown',
                'country': 'Unknown',
                'timezone': 'Unknown'
            }
            
            # Get carrier information from v1 API response
            carrier_info = phone_number_object.carrier
            if carrier_info:
                # Check for error codes
                error_code = carrier_info.get('error_code')
                if error_code:
                    logger.warning(f"Twilio carrier lookup error {error_code} for {phone_number}")
                    # If there's an error, we'll fall back to phonenumbers detection
                    return None
                
                result['carrier'] = carrier_info.get('name', 'Unknown')
                result['carrier_type'] = carrier_info.get('type', 'Unknown')
                
                # Determine line type from carrier type
                carrier_type = carrier_info.get('type', '').lower()
                if carrier_type == 'mobile':
                    result['line_type'] = 'Mobile'
                    result['is_mobile'] = True
                elif carrier_type == 'landline':
                    result['line_type'] = 'Landline'
                    result['is_landline'] = True
                elif carrier_type == 'voip':
                    result['line_type'] = 'VoIP'
                    result['is_voip'] = True
                elif carrier_type == 'toll_free':
                    result['line_type'] = 'Toll-Free'
                    result['is_toll_free'] = True
                else:
                    result['line_type'] = 'Unknown'
            
            # Note: line_type_intelligence is not available in v1 API
            # We rely entirely on Twilio's carrier type information for line type detection
            # Twilio provides accurate carrier type: mobile, landline, voip, toll_free
            
            # Get location information using phonenumbers
            try:
                parsed = phonenumbers.parse(phone_number, "US")
                location = geocoder.description_for_number(parsed, "en")
                result['location'] = location if location else 'Unknown'
                
                country = geocoder.country_name_for_number(parsed, "en")
                result['country'] = country if country else 'Unknown'
                
                time_zones = timezone.time_zones_for_number(parsed)
                result['timezone'] = ', '.join(time_zones) if time_zones else 'Unknown'
            except:
                pass
            
            return result
            
        except Exception as e:
            logger.warning(f"Twilio Lookup API error for {phone_number}: {e}")
            return None
    
    def _get_enhanced_phonenumbers_info(self, parsed_number):
        """Get enhanced information using phonenumbers library with VoIP detection"""
        result = {}
        
        try:
            result['is_valid'] = phonenumbers.is_valid_number(parsed_number)
            if not result['is_valid']:
                return result
            
            result['formatted_phone'] = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            
            # Get number type
            from phonenumbers.phonenumberutil import number_type, PhoneNumberType
            number_type_enum = number_type(parsed_number)
            
            result['is_mobile'] = number_type_enum == PhoneNumberType.MOBILE
            result['is_landline'] = number_type_enum == PhoneNumberType.FIXED_LINE
            result['is_voip'] = number_type_enum == PhoneNumberType.VOIP
            result['is_toll_free'] = number_type_enum == PhoneNumberType.TOLL_FREE
            
            # Determine line type
            if result['is_mobile']:
                result['line_type'] = 'Mobile'
            elif result['is_landline']:
                result['line_type'] = 'Landline'
            elif result['is_voip']:
                result['line_type'] = 'VoIP'
            elif result['is_toll_free']:
                result['line_type'] = 'Toll-Free'
            else:
                result['line_type'] = 'Unknown'
            
            # Get carrier information
            carrier_name = carrier.name_for_number(parsed_number, "en")
            result['carrier'] = carrier_name if carrier_name else 'Unknown'
            result['carrier_type'] = result['line_type']
            
            # Get location information
            location = geocoder.description_for_number(parsed_number, "en")
            result['location'] = location if location else 'Unknown'
            
            country = geocoder.country_name_for_number(parsed_number, "en")
            result['country'] = country if country else 'Unknown'
            
            time_zones = timezone.time_zones_for_number(parsed_number)
            result['timezone'] = ', '.join(time_zones) if time_zones else 'Unknown'
            
            # Note: For fallback phonenumbers detection, we rely on the library's built-in type detection
            # No additional manual VoIP detection needed since phonenumbers library handles this
            
        except Exception as e:
            result['error'] = f'Phonenumbers parse error: {str(e)}'
            result['is_valid'] = False
        
        return result
    
    def get_phone_summary(self, validation_results):
        """Get summary statistics for phone validation results"""
        total = len(validation_results)
        valid = len(validation_results[validation_results['is_valid'] == True])
        invalid = total - valid
        
        mobile = len(validation_results[validation_results.get('is_mobile', False) == True])
        landline = len(validation_results[validation_results.get('is_landline', False) == True])
        voip = len(validation_results[validation_results.get('is_voip', False) == True])
        toll_free = len(validation_results[validation_results.get('is_toll_free', False) == True])
        
        can_sms = len(validation_results[validation_results.get('can_receive_sms', False) == True])
        can_whatsapp = len(validation_results[validation_results.get('can_receive_whatsapp', False) == True])
        
        return {
            'total': total,
            'valid': valid,
            'invalid': invalid,
            'mobile': mobile,
            'landline': landline,
            'voip': voip,
            'toll_free': toll_free,
            'can_receive_sms': can_sms,
            'can_receive_whatsapp': can_whatsapp
        }

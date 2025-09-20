"""
Enhanced phone number validation module with multiple detection methods
Uses Twilio Lookup API, Abstract API, and improved heuristics for better phone type detection
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

# Load environment variables
load_dotenv('config.env')

logger = get_logger()

class EnhancedPhoneValidator:
    def __init__(self):
        self.carrier_cache = {}
        self.twilio_client = None
        self.abstract_api_key = os.getenv('ABSTRACT_API_KEY')
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
        
        # VoIP carrier patterns (common VoIP providers)
        self.voip_carriers = {
            'google voice', 'google fi', 'ringcentral', 'vonage', 'skype', 'whatsapp',
            'telegram', 'discord', 'zoom', 'microsoft teams', 'slack', 'twilio',
            'bandwidth', 'flowroute', 'voip.ms', 'callcentric', 'voipfone',
            'grasshopper', 'nextiva', '8x8', 'jive', 'mightycall', 'phone.com'
        }
        
        # VoIP number patterns (common VoIP number ranges)
        self.voip_patterns = [
            # Google Voice patterns
            r'^\+1(?:206|253|425|360|564|509|360|425|253|206)',  # Washington state
            r'^\+1(?:415|628|510|925|650|408|669|707|831|209)',  # California
            r'^\+1(?:646|212|718|347|929|516|631|845|914|607)',  # New York
            # Common VoIP ranges
            r'^\+1(?:800|833|844|855|866|877|888)',  # Toll-free (often used by VoIP)
            r'^\+1(?:900|976)',  # Premium rate (sometimes VoIP)
        ]
    
    def validate_phones(self, df, progress_callback=None, use_multithreading=True, max_workers=10):
        """Enhanced phone validation with multiple detection methods"""
        if use_multithreading:
            return self._validate_phones_multithreaded(df, progress_callback, max_workers)
        else:
            return self._validate_phones_sequential(df, progress_callback)
    
    def _validate_phones_sequential(self, df, progress_callback=None):
        """Sequential enhanced phone validation"""
        results = []
        total_phones = len(df)
        processed = 0
        
        for idx, row in df.iterrows():
            phone = row.get('Phone', '')
            name = row.get('Name', '')
            
            result = {
                'index': idx,
                'name': name,
                'original_phone': phone,
                'formatted_phone': '',
                'is_valid': False,
                'carrier': 'Unknown',
                'location': 'Unknown',
                'country': 'Unknown',
                'error': '',
                'carrier_type': 'Unknown',
                'line_type': 'Unknown',
                'is_mobile': False,
                'is_landline': False,
                'is_voip': False,
                'is_toll_free': False,
                'confidence': 0,
                'detection_method': 'none'
            }
            
            if phone and phone != 'nan':
                try:
                    # Parse phone number
                    parsed = phonenumbers.parse(phone, "US")
                    
                    if phonenumbers.is_valid_number(parsed):
                        result['is_valid'] = True
                        result['formatted_phone'] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                        
                        # Enhanced detection using multiple methods
                        enhanced_info = self._get_enhanced_carrier_info(parsed, phone)
                        result.update(enhanced_info)
                        
                        # Get location information
                        location = geocoder.description_for_number(parsed, "en")
                        result['location'] = location if location else 'Unknown'
                        
                        # Get country
                        country = geocoder.country_name_for_number(parsed, "en")
                        result['country'] = country if country else 'Unknown'
                        
                        # Get timezone
                        time_zones = timezone.time_zones_for_number(parsed)
                        result['timezone'] = ', '.join(time_zones) if time_zones else 'Unknown'
                        
                    else:
                        result['error'] = 'Invalid phone number format'
                        
                except Exception as e:
                    result['error'] = f'Parse error: {str(e)}'
            
            results.append(result)
            processed += 1
            
            # Add small delay to avoid rate limiting
            time.sleep(0.1)
            
            if progress_callback:
                progress_callback(min(processed, total_phones), total_phones)
        
        return pd.DataFrame(results)
    
    def _validate_phones_multithreaded(self, df, progress_callback=None, max_workers=10):
        """Multithreaded enhanced phone validation"""
        import concurrent.futures
        import threading
        
        # Prepare data for multithreading
        phone_data_list = []
        for idx, row in df.iterrows():
            phone_data_list.append({
                'index': idx,
                'row': row.to_dict()
            })
        
        # Thread-safe progress tracking
        progress_lock = threading.Lock()
        processed_count = 0
        results = []
        
        def validate_single_phone(phone_data_item):
            nonlocal processed_count
            
            idx = phone_data_item['index']
            row = phone_data_item['row']
            phone = row.get('Phone', '')
            name = row.get('Name', '')
            
            result = {
                'index': idx,
                'name': name,
                'original_phone': phone,
                'formatted_phone': '',
                'is_valid': False,
                'carrier': 'Unknown',
                'location': 'Unknown',
                'country': 'Unknown',
                'error': '',
                'carrier_type': 'Unknown',
                'line_type': 'Unknown',
                'is_mobile': False,
                'is_landline': False,
                'is_voip': False,
                'is_toll_free': False,
                'confidence': 0,
                'detection_method': 'none'
            }
            
            if phone and phone != 'nan':
                try:
                    # Parse phone number
                    parsed = phonenumbers.parse(phone, "US")
                    
                    if phonenumbers.is_valid_number(parsed):
                        result['is_valid'] = True
                        result['formatted_phone'] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                        
                        # Enhanced detection using multiple methods
                        enhanced_info = self._get_enhanced_carrier_info(parsed, phone)
                        result.update(enhanced_info)
                        
                        # Get location information
                        location = geocoder.description_for_number(parsed, "en")
                        result['location'] = location if location else 'Unknown'
                        
                        # Get country
                        country = geocoder.country_name_for_number(parsed, "en")
                        result['country'] = country if country else 'Unknown'
                        
                    else:
                        result['error'] = 'Invalid phone number format'
                        
                except Exception as e:
                    result['error'] = str(e)
            
            # Update progress thread-safely
            with progress_lock:
                processed_count += 1
                if progress_callback and processed_count % 5 == 0:
                    progress_callback(min(processed_count, len(phone_data_list)), len(phone_data_list))
            
            return result
        
        # Execute with ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_data = {executor.submit(validate_single_phone, phone_item): phone_item for phone_item in phone_data_list}
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_data):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # Handle any exceptions from individual phone validation
                    phone_item = future_to_data[future]
                    results.append({
                        'index': phone_item['index'],
                        'name': phone_item['row'].get('Name', ''),
                        'original_phone': phone_item['row'].get('Phone', ''),
                        'is_valid': False,
                        'error': f'Validation error: {str(e)}',
                        'detection_method': 'error'
                    })
        
        # Final progress update
        if progress_callback:
            progress_callback(len(phone_data_list), len(phone_data_list))
        
        return pd.DataFrame(results)
    
    def _get_enhanced_carrier_info(self, parsed_number, original_phone):
        """Get enhanced carrier information using multiple detection methods"""
        result = {
            'carrier': 'Unknown',
            'carrier_type': 'Unknown',
            'line_type': 'Unknown',
            'is_mobile': False,
            'is_landline': False,
            'is_voip': False,
            'is_toll_free': False,
            'confidence': 0,
            'detection_method': 'phonenumbers'
        }
        
        # Method 1: Twilio Lookup API (most accurate)
        twilio_info = self._get_twilio_carrier_info(parsed_number)
        if twilio_info['success']:
            result.update(twilio_info['data'])
            result['detection_method'] = 'twilio_lookup'
            result['confidence'] = 95
            return result
        
        # Method 2: Abstract API (backup)
        abstract_info = self._get_abstract_carrier_info(original_phone)
        if abstract_info['success']:
            result.update(abstract_info['data'])
            result['detection_method'] = 'abstract_api'
            result['confidence'] = 85
            return result
        
        # Method 3: Enhanced phonenumbers with heuristics
        enhanced_phonenumbers = self._get_enhanced_phonenumbers_info(parsed_number, original_phone)
        result.update(enhanced_phonenumbers)
        result['confidence'] = enhanced_phonenumbers.get('confidence', 60)
        
        return result
    
    def _get_twilio_carrier_info(self, parsed_number):
        """Get carrier information from Twilio Lookup API"""
        if not self.twilio_client:
            return {'success': False, 'error': 'Twilio client not available'}
        
        try:
            formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            
            # Use Twilio Lookup API
            phone_number = self.twilio_client.lookups.v1.phone_numbers(formatted_number).fetch(
                type=['carrier']
            )
            
            carrier_info = phone_number.carrier
            
            result = {
                'carrier': carrier_info.get('name', 'Unknown'),
                'carrier_type': carrier_info.get('type', 'Unknown'),
                'line_type': carrier_info.get('type', 'Unknown'),
                'is_mobile': carrier_info.get('type', '').lower() == 'mobile',
                'is_landline': carrier_info.get('type', '').lower() in ['landline', 'fixed-line'],
                'is_voip': carrier_info.get('type', '').lower() == 'voip',
                'is_toll_free': carrier_info.get('type', '').lower() == 'toll-free'
            }
            
            # Additional VoIP detection based on carrier name
            carrier_name = carrier_info.get('name', '')
            if carrier_name and any(voip_carrier in carrier_name.lower() for voip_carrier in self.voip_carriers):
                result['is_voip'] = True
                result['line_type'] = 'VoIP'
            
            return {'success': True, 'data': result}
            
        except Exception as e:
            logger.warning(f"Twilio Lookup API error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_abstract_carrier_info(self, phone_number):
        """Get carrier information from Abstract API"""
        if not self.abstract_api_key:
            return {'success': False, 'error': 'Abstract API key not available'}
        
        try:
            url = f"https://phonevalidation.abstractapi.com/v1/"
            params = {
                'api_key': self.abstract_api_key,
                'phone': phone_number
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('valid', False):
                result = {
                    'carrier': data.get('carrier', 'Unknown'),
                    'carrier_type': data.get('line_type', 'Unknown'),
                    'line_type': data.get('line_type', 'Unknown'),
                    'is_mobile': data.get('line_type', '').lower() == 'mobile',
                    'is_landline': data.get('line_type', '').lower() in ['landline', 'fixed-line'],
                    'is_voip': data.get('line_type', '').lower() == 'voip',
                    'is_toll_free': data.get('line_type', '').lower() == 'toll-free'
                }
                
                return {'success': True, 'data': result}
            else:
                return {'success': False, 'error': 'Invalid phone number'}
                
        except Exception as e:
            logger.warning(f"Abstract API error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_enhanced_phonenumbers_info(self, parsed_number, original_phone):
        """Enhanced phonenumbers detection with better heuristics"""
        result = {
            'carrier': 'Unknown',
            'carrier_type': 'Unknown',
            'line_type': 'Unknown',
            'is_mobile': False,
            'is_landline': False,
            'is_voip': False,
            'is_toll_free': False,
            'confidence': 60
        }
        
        try:
            # Basic carrier information
            carrier_name = carrier.name_for_number(parsed_number, "en")
            
            # Get number type
            number_type = phonenumbers.number_type(parsed_number)
            
            # Enhanced carrier detection
            enhanced_carrier = self._get_enhanced_carrier_name(carrier_name, original_phone)
            
            # Determine line type with better heuristics
            line_type = self._determine_line_type(number_type, carrier_name, original_phone)
            
            result.update({
                'carrier': enhanced_carrier,
                'carrier_type': self._get_carrier_type_description(number_type),
                'line_type': line_type,
                'is_mobile': number_type == phonenumbers.PhoneNumberType.MOBILE,
                'is_landline': number_type == phonenumbers.PhoneNumberType.FIXED_LINE,
                'is_voip': self._is_voip_number(number_type, carrier_name, original_phone),
                'is_toll_free': number_type == phonenumbers.PhoneNumberType.TOLL_FREE,
                'confidence': self._calculate_confidence(number_type, carrier_name, original_phone)
            })
            
        except Exception as e:
            logger.warning(f"Enhanced phonenumbers error: {e}")
            result['error'] = str(e)
        
        return result
    
    def _get_enhanced_carrier_name(self, carrier_name, original_phone):
        """Get enhanced carrier name with better detection"""
        if not carrier_name or carrier_name == 'Unknown':
            # Try to detect carrier from phone number patterns
            if original_phone.startswith('+1'):
                # US number - try to detect carrier from area code
                area_code = original_phone[2:5]
                carrier_name = self._detect_carrier_from_area_code(area_code)
        
        return carrier_name if carrier_name else 'Unknown'
    
    def _detect_carrier_from_area_code(self, area_code):
        """Detect carrier from area code patterns (basic heuristic)"""
        # This is a simplified heuristic - in practice, you'd need a comprehensive database
        area_code_carriers = {
            '206': 'AT&T', '253': 'Verizon', '425': 'T-Mobile', '360': 'Sprint',
            '415': 'AT&T', '510': 'Verizon', '925': 'T-Mobile', '650': 'Sprint',
            '646': 'AT&T', '212': 'Verizon', '718': 'T-Mobile', '347': 'Sprint'
        }
        return area_code_carriers.get(area_code, 'Unknown')
    
    def _determine_line_type(self, number_type, carrier_name, original_phone):
        """Determine line type with enhanced heuristics"""
        # Check for VoIP based on carrier name
        if carrier_name and any(voip_carrier in carrier_name.lower() for voip_carrier in self.voip_carriers):
            return 'VoIP'
        
        # Check for VoIP based on number patterns
        if self._matches_voip_pattern(original_phone):
            return 'VoIP'
        
        # Use phonenumbers type
        if number_type == phonenumbers.PhoneNumberType.MOBILE:
            return 'Mobile'
        elif number_type == phonenumbers.PhoneNumberType.FIXED_LINE:
            return 'Landline'
        elif number_type == phonenumbers.PhoneNumberType.VOIP:
            return 'VoIP'
        elif number_type == phonenumbers.PhoneNumberType.TOLL_FREE:
            return 'Toll-Free'
        else:
            return 'Unknown'
    
    def _is_voip_number(self, number_type, carrier_name, original_phone):
        """Enhanced VoIP detection"""
        # Direct VoIP type from phonenumbers
        if number_type == phonenumbers.PhoneNumberType.VOIP:
            return True
        
        # Check carrier name for VoIP indicators
        if carrier_name and any(voip_carrier in carrier_name.lower() for voip_carrier in self.voip_carriers):
            return True
        
        # Check number patterns
        if self._matches_voip_pattern(original_phone):
            return True
        
        return False
    
    def _matches_voip_pattern(self, phone_number):
        """Check if phone number matches VoIP patterns"""
        import re
        for pattern in self.voip_patterns:
            if re.match(pattern, phone_number):
                return True
        return False
    
    def _get_carrier_type_description(self, number_type):
        """Get human-readable carrier type description"""
        type_descriptions = {
            phonenumbers.PhoneNumberType.MOBILE: 'Mobile',
            phonenumbers.PhoneNumberType.FIXED_LINE: 'Landline',
            phonenumbers.PhoneNumberType.VOIP: 'VoIP',
            phonenumbers.PhoneNumberType.TOLL_FREE: 'Toll-Free',
            phonenumbers.PhoneNumberType.PREMIUM_RATE: 'Premium Rate',
            phonenumbers.PhoneNumberType.SHARED_COST: 'Shared Cost',
            phonenumbers.PhoneNumberType.PERSONAL_NUMBER: 'Personal Number',
            phonenumbers.PhoneNumberType.PAGER: 'Pager',
            phonenumbers.PhoneNumberType.UAN: 'UAN',
            phonenumbers.PhoneNumberType.UNKNOWN: 'Unknown'
        }
        return type_descriptions.get(number_type, 'Unknown')
    
    def _calculate_confidence(self, number_type, carrier_name, original_phone):
        """Calculate confidence score for the detection"""
        confidence = 60  # Base confidence
        
        # Increase confidence if we have carrier name
        if carrier_name and carrier_name != 'Unknown':
            confidence += 20
        
        # Increase confidence for clear number types
        if number_type in [phonenumbers.PhoneNumberType.MOBILE, phonenumbers.PhoneNumberType.FIXED_LINE]:
            confidence += 15
        
        # Increase confidence for VoIP detection
        if self._is_voip_number(number_type, carrier_name, original_phone):
            confidence += 10
        
        return min(confidence, 100)

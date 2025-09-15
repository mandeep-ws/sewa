"""
Phone number validation module with carrier information
"""

import pandas as pd
import streamlit as st
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import requests
import time
import json

class PhoneValidator:
    def __init__(self):
        self.carrier_cache = {}
    
    def validate_phones(self, df, progress_callback=None):
        """Validate phone numbers and get carrier information"""
        results = []
        
        total_phones = len(df[df['Phone'].notna() & (df['Phone'] != '')])
        processed = 0
        
        for idx, row in df.iterrows():
            if idx % 10 == 0 and progress_callback:
                progress_callback(min(processed, total_phones), total_phones)
            
            phone = str(row['Phone']) if pd.notna(row['Phone']) else ''
            
            result = {
                'index': idx,
                'name': row.get('Name', ''),
                'original_phone': phone,
                'formatted_phone': '',
                'is_valid': False,
                'carrier': '',
                'location': '',
                'country': '',
                'error': ''
            }
            
            if phone and phone != 'nan':
                try:
                    # Parse phone number
                    parsed = phonenumbers.parse(phone, "US")
                    
                    if phonenumbers.is_valid_number(parsed):
                        result['is_valid'] = True
                        result['formatted_phone'] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                        
                        # Get detailed carrier information
                        carrier_info = self._get_detailed_carrier_info(parsed)
                        result.update(carrier_info)
                        
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
    
    def _get_detailed_carrier_info(self, parsed_number):
        """Get detailed carrier information for a phone number"""
        try:
            # Basic carrier information
            carrier_name = carrier.name_for_number(parsed_number, "en")
            
            # Get number type (this is the correct way to get carrier type)
            number_type = phonenumbers.number_type(parsed_number)
            
            # Try to get better carrier information
            enhanced_carrier = self._get_enhanced_carrier_info(parsed_number)
            
            # Additional carrier details
            carrier_info = {
                'carrier': enhanced_carrier if enhanced_carrier else (carrier_name if carrier_name else 'Unknown'),
                'carrier_type': self._get_carrier_type_description(number_type),
                'line_type': self._get_line_type_description(parsed_number),
                'is_mobile': number_type == phonenumbers.PhoneNumberType.MOBILE,
                'is_landline': number_type == phonenumbers.PhoneNumberType.FIXED_LINE,
                'is_voip': number_type == phonenumbers.PhoneNumberType.VOIP,
                'is_toll_free': number_type == phonenumbers.PhoneNumberType.TOLL_FREE,
                'is_premium_rate': number_type == phonenumbers.PhoneNumberType.PREMIUM_RATE,
                'is_shared_cost': number_type == phonenumbers.PhoneNumberType.SHARED_COST,
                'is_personal_number': number_type == phonenumbers.PhoneNumberType.PERSONAL_NUMBER,
                'is_pager': number_type == phonenumbers.PhoneNumberType.PAGER,
                'is_uan': number_type == phonenumbers.PhoneNumberType.UAN,
                'is_unknown': number_type == phonenumbers.PhoneNumberType.UNKNOWN
            }
            
            # Try to get additional carrier details from external API
            try:
                additional_info = self._get_carrier_details_from_api(parsed_number)
                carrier_info.update(additional_info)
            except:
                pass  # Continue without additional info if API fails
            
            return carrier_info
            
        except Exception as e:
            return {
                'carrier': 'Unknown',
                'carrier_type': 'Unknown',
                'line_type': 'Unknown',
                'error': f'Carrier info error: {str(e)}'
            }
    
    def _get_carrier_type_description(self, number_type):
        """Get human-readable carrier type description"""
        type_map = {
            phonenumbers.PhoneNumberType.MOBILE: 'Mobile',
            phonenumbers.PhoneNumberType.FIXED_LINE: 'Fixed Line',
            phonenumbers.PhoneNumberType.VOIP: 'VoIP',
            phonenumbers.PhoneNumberType.TOLL_FREE: 'Toll Free',
            phonenumbers.PhoneNumberType.PREMIUM_RATE: 'Premium Rate',
            phonenumbers.PhoneNumberType.SHARED_COST: 'Shared Cost',
            phonenumbers.PhoneNumberType.PERSONAL_NUMBER: 'Personal Number',
            phonenumbers.PhoneNumberType.PAGER: 'Pager',
            phonenumbers.PhoneNumberType.UAN: 'Universal Access Number',
            phonenumbers.PhoneNumberType.UNKNOWN: 'Unknown'
        }
        return type_map.get(number_type, 'Unknown')
    
    def _get_enhanced_carrier_info(self, parsed_number):
        """Try to get enhanced carrier information using multiple methods"""
        try:
            # Method 1: Try different regions for carrier name
            for region in ["US", "en", "en-US"]:
                carrier_name = carrier.name_for_number(parsed_number, region)
                if carrier_name and carrier_name != "Unknown":
                    return carrier_name
            
            # Method 2: Try to identify carrier by area code and prefix patterns
            formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
            carrier_by_pattern = self._identify_carrier_by_pattern(formatted_number)
            if carrier_by_pattern:
                return carrier_by_pattern
            
            # Method 3: Use external API if available
            try:
                external_carrier = self._get_carrier_from_external_api(parsed_number)
                if external_carrier:
                    return external_carrier
            except:
                pass
            
            return None
            
        except Exception as e:
            return None
    
    def _identify_carrier_by_pattern(self, formatted_number):
        """Identify carrier by phone number patterns (area code and prefix)"""
        try:
            # Remove all non-digit characters
            digits = ''.join(filter(str.isdigit, formatted_number))
            
            if len(digits) >= 10:
                area_code = digits[:3]
                prefix = digits[3:6]
                
                # Common carrier patterns (this is a simplified approach)
                # Note: This is not 100% accurate as number portability makes it complex
                carrier_patterns = {
                    # Verizon patterns (simplified)
                    '201': 'Verizon', '202': 'Verizon', '203': 'Verizon',
                    # AT&T patterns (simplified)  
                    '205': 'AT&T', '206': 'AT&T', '207': 'AT&T',
                    # T-Mobile patterns (simplified)
                    '208': 'T-Mobile', '209': 'T-Mobile', '210': 'T-Mobile',
                    # Sprint patterns (simplified)
                    '212': 'Sprint', '213': 'Sprint', '214': 'Sprint',
                }
                
                # Check area code patterns
                if area_code in carrier_patterns:
                    return carrier_patterns[area_code]
                
                # Additional logic could be added here for more sophisticated detection
                # For now, return None to fall back to other methods
                return None
                
        except Exception as e:
            return None
    
    def _get_carrier_from_external_api(self, parsed_number):
        """Get carrier information from external API (placeholder for future implementation)"""
        # This could be implemented with services like:
        # - Twilio Lookup API
        # - NumVerify API
        # - Abstract API
        # For now, return None
        return None
    
    def _get_line_type_description(self, parsed_number):
        """Get line type description"""
        number_type = phonenumbers.number_type(parsed_number)
        type_map = {
            phonenumbers.PhoneNumberType.MOBILE: 'Mobile',
            phonenumbers.PhoneNumberType.FIXED_LINE: 'Fixed Line',
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: 'Fixed Line or Mobile',
            phonenumbers.PhoneNumberType.TOLL_FREE: 'Toll Free',
            phonenumbers.PhoneNumberType.PREMIUM_RATE: 'Premium Rate',
            phonenumbers.PhoneNumberType.SHARED_COST: 'Shared Cost',
            phonenumbers.PhoneNumberType.VOIP: 'VoIP',
            phonenumbers.PhoneNumberType.PERSONAL_NUMBER: 'Personal Number',
            phonenumbers.PhoneNumberType.PAGER: 'Pager',
            phonenumbers.PhoneNumberType.UAN: 'Universal Access Number',
            phonenumbers.PhoneNumberType.UNKNOWN: 'Unknown'
        }
        return type_map.get(number_type, 'Unknown')
    
    def _get_carrier_details_from_api(self, parsed_number):
        """Get additional carrier details from external API (optional)"""
        # This is a placeholder for additional carrier information
        # You can integrate with services like Twilio Lookup API, NumVerify, etc.
        phone_str = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        
        # Example: You could use Twilio Lookup API here
        # For now, return basic additional info
        return {
            'formatted_national': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL),
            'formatted_international': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            'country_code': parsed_number.country_code,
            'national_number': parsed_number.national_number,
            'extension': parsed_number.extension if parsed_number.extension else None
        }
    
    def get_carrier_info(self, phone_number):
        """Get detailed carrier information for a phone number"""
        try:
            parsed = phonenumbers.parse(phone_number, "US")
            
            if not phonenumbers.is_valid_number(parsed):
                return None
            
            # Get carrier information
            carrier_name = carrier.name_for_number(parsed, "en")
            carrier_type = carrier.carrier_type_for_number(parsed)
            
            return {
                'carrier': carrier_name,
                'type': carrier_type,
                'formatted': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def check_fraud_indicators(self, phone_number):
        """Check for potential fraud indicators"""
        fraud_indicators = []
        
        try:
            parsed = phonenumbers.parse(phone_number, "US")
            
            # Check for suspicious patterns
            number_str = str(parsed.national_number)
            
            # Check for repeated digits
            if len(set(number_str)) < 3:
                fraud_indicators.append("Repeated digits pattern")
            
            # Check for sequential digits
            if number_str in ['1234567890', '0123456789']:
                fraud_indicators.append("Sequential digits")
            
            # Check for all same digits
            if len(set(number_str)) == 1:
                fraud_indicators.append("All same digits")
            
            # Check for common test numbers
            test_numbers = ['5555555555', '1234567890', '0000000000']
            if number_str in test_numbers:
                fraud_indicators.append("Test number")
            
        except Exception as e:
            fraud_indicators.append(f"Parse error: {str(e)}")
        
        return fraud_indicators
    
    def format_phone_display(self, phone_number):
        """Format phone number for display"""
        try:
            parsed = phonenumbers.parse(phone_number, "US")
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
        except:
            return phone_number

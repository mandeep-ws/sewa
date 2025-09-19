"""
Address validation module using Google Geocoding API
"""

import pandas as pd
import streamlit as st
import googlemaps
import time
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from config.env
load_dotenv('config.env')

class AddressValidator:
    def __init__(self):
        # Initialize Google Maps client
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if api_key:
            self.gmaps = googlemaps.Client(key=api_key)
        else:
            self.gmaps = None
            st.warning("⚠️ Google Maps API key not found. Please set GOOGLE_MAPS_API_KEY environment variable.")
    
    def validate_addresses(self, df, progress_callback=None, use_multithreading=True, max_workers=2, api_delay=0.5):
        """Validate addresses using Google Geocoding API"""
        if not self.gmaps:
            st.error("❌ Google Maps API not configured. Cannot validate addresses.")
            return pd.DataFrame()
        
        if use_multithreading:
            return self._validate_addresses_multithreaded(df, progress_callback, max_workers, api_delay)
        else:
            return self._validate_addresses_sequential(df, progress_callback, api_delay)
    
    def _validate_addresses_sequential(self, df, progress_callback=None, api_delay=0.5):
        """Original sequential address validation"""
        results = []
        total_addresses = len(df[df['Address'].notna() & (df['Address'] != '')])
        processed = 0
        
        for idx, row in df.iterrows():
            if idx % 5 == 0 and progress_callback:  # Update progress every 5 addresses
                progress_callback(min(processed, total_addresses), total_addresses)
            
            address = str(row['Address']) if pd.notna(row['Address']) else ''
            
            result = {
                'index': idx,
                'name': row.get('Name', ''),
                'original_address': address,
                'formatted_address': '',
                'is_valid': False,
                'components': {},
                'coordinates': {},
                'confidence': 0,
                'error': ''
            }
            
            if address and address != 'nan':
                try:
                    # Geocode the address with retry logic
                    max_retries = 3
                    geocode_result = None
                    
                    for attempt in range(max_retries):
                        try:
                            geocode_result = self.gmaps.geocode(address)
                            break
                        except Exception as e:
                            if attempt < max_retries - 1:
                                # Wait longer before retry (increased delay)
                                time.sleep(1.0 * (attempt + 1))
                                continue
                            else:
                                raise e
                    
                    if geocode_result:
                        # Get the first (most relevant) result
                        first_result = geocode_result[0]
                        
                        result['is_valid'] = True
                        result['formatted_address'] = first_result['formatted_address']
                        result['confidence'] = self._calculate_confidence(first_result)
                        
                        # Extract components
                        components = first_result.get('address_components', [])
                        result['components'] = self._extract_components(components)
                        
                        # Extract coordinates
                        geometry = first_result.get('geometry', {})
                        location = geometry.get('location', {})
                        result['coordinates'] = {
                            'lat': location.get('lat'),
                            'lng': location.get('lng')
                        }
                        
                    else:
                        result['error'] = 'Address not found'
                        
                except Exception as e:
                    error_msg = str(e)
                    # Log the error for debugging
                    print(f"🔍 Address validation error for '{address}': {error_msg}")
                    
                    # Provide more specific error messages
                    if 'OVER_QUERY_LIMIT' in error_msg:
                        result['error'] = 'API quota exceeded - please try again later'
                    elif 'REQUEST_DENIED' in error_msg:
                        result['error'] = 'API request denied - check API key'
                    elif 'INVALID_REQUEST' in error_msg:
                        result['error'] = 'Invalid address format'
                    elif 'ZERO_RESULTS' in error_msg:
                        result['error'] = 'Address not found'
                    elif 'UNKNOWN_ERROR' in error_msg:
                        result['error'] = 'Temporary API error - please retry'
                    else:
                        result['error'] = f'Geocoding error: {error_msg}'
            
            results.append(result)
            processed += 1
            
            # Add delay to respect API rate limits (configurable delay)
            time.sleep(api_delay)
        
        if progress_callback:
            progress_callback(min(processed, total_addresses), total_addresses)
        
        return pd.DataFrame(results)
    
    def _validate_addresses_multithreaded(self, df, progress_callback=None, max_workers=2, api_delay=0.5):
        """Multithreaded address validation for better performance"""
        import concurrent.futures
        import threading
        
        # Prepare data for multithreading
        address_data = []
        for idx, row in df.iterrows():
            address_data.append({
                'index': idx,
                'name': row.get('Name', ''),
                'address': str(row['Address']) if pd.notna(row['Address']) else ''
            })
        
        # Filter out empty addresses
        address_data = [data for data in address_data if data['address'] and data['address'] != 'nan']
        total_addresses = len(address_data)
        
        if total_addresses == 0:
            return pd.DataFrame()
        
        # Thread-safe progress tracking
        progress_lock = threading.Lock()
        processed_count = 0
        
        def validate_single_address(address_data_item):
            nonlocal processed_count
            
            idx = address_data_item['index']
            name = address_data_item['name']
            address = address_data_item['address']
            
            result = {
                'index': idx,
                'name': name,
                'original_address': address,
                'formatted_address': '',
                'is_valid': False,
                'components': {},
                'coordinates': {},
                'confidence': 0,
                'error': ''
            }
            
            # Add rate limiting for multithreaded requests (configurable delay)
            time.sleep(api_delay)
            
            try:
                # Geocode the address with retry logic
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        geocode_result = self.gmaps.geocode(address)
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            # Wait longer before retry (increased delay)
                            time.sleep(1.0 * (attempt + 1))
                            continue
                        else:
                            raise e
                
                if geocode_result:
                    # Get the first (most relevant) result
                    first_result = geocode_result[0]
                    
                    result['is_valid'] = True
                    result['formatted_address'] = first_result['formatted_address']
                    result['confidence'] = self._calculate_confidence(first_result)
                    
                    # Extract components
                    components = first_result.get('address_components', [])
                    result['components'] = self._extract_components(components)
                    
                    # Extract coordinates
                    geometry = first_result.get('geometry', {})
                    location = geometry.get('location', {})
                    result['coordinates'] = {
                        'lat': location.get('lat'),
                        'lng': location.get('lng')
                    }
                    
                else:
                    result['error'] = 'Address not found'
                    
            except Exception as e:
                error_msg = str(e)
                # Log the error for debugging
                print(f"🔍 Address validation error for '{address}': {error_msg}")
                
                # Provide more specific error messages
                if 'OVER_QUERY_LIMIT' in error_msg:
                    result['error'] = 'API quota exceeded - please try again later'
                elif 'REQUEST_DENIED' in error_msg:
                    result['error'] = 'API request denied - check API key'
                elif 'INVALID_REQUEST' in error_msg:
                    result['error'] = 'Invalid address format'
                elif 'ZERO_RESULTS' in error_msg:
                    result['error'] = 'Address not found'
                elif 'UNKNOWN_ERROR' in error_msg:
                    result['error'] = 'Temporary API error - please retry'
                else:
                    result['error'] = f'Geocoding error: {error_msg}'
            
            # Update progress thread-safely
            with progress_lock:
                processed_count += 1
                if progress_callback and processed_count % 2 == 0:  # Update every 2 addresses
                    progress_callback(min(processed_count, total_addresses), total_addresses)
            
            return result
        
        # Execute with ThreadPoolExecutor
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_data = {executor.submit(validate_single_address, data): data for data in address_data}
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_data):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # Handle any exceptions from individual address validations
                    data = future_to_data[future]
                    results.append({
                        'index': data['index'],
                        'name': data['name'],
                        'original_address': data['address'],
                        'formatted_address': '',
                        'is_valid': False,
                        'components': {},
                        'coordinates': {},
                        'confidence': 0,
                        'error': f'Validation error: {str(e)}'
                    })
        
        # Final progress update
        if progress_callback:
            progress_callback(total_addresses, total_addresses)
        
        return pd.DataFrame(results)
    
    def _calculate_confidence(self, geocode_result):
        """Calculate confidence score based on geocoding result"""
        confidence = 0
        
        # Check geometry type
        geometry = geocode_result.get('geometry', {})
        location_type = geometry.get('location_type', '')
        
        if location_type == 'ROOFTOP':
            confidence += 40
        elif location_type == 'RANGE_INTERPOLATED':
            confidence += 30
        elif location_type == 'GEOMETRIC_CENTER':
            confidence += 20
        elif location_type == 'APPROXIMATE':
            confidence += 10
        
        # Check partial match
        if not geocode_result.get('partial_match', False):
            confidence += 30
        
        # Check address components completeness
        components = geocode_result.get('address_components', [])
        required_types = ['street_number', 'route', 'locality', 'administrative_area_level_1', 'postal_code']
        
        found_types = [comp.get('types', []) for comp in components]
        found_types = [item for sublist in found_types for item in sublist]
        
        for req_type in required_types:
            if req_type in found_types:
                confidence += 6
        
        return min(confidence, 100)
    
    def _extract_components(self, components):
        """Extract address components from geocoding result"""
        extracted = {}
        
        for component in components:
            types = component.get('types', [])
            long_name = component.get('long_name', '')
            short_name = component.get('short_name', '')
            
            if 'street_number' in types:
                extracted['street_number'] = long_name
            elif 'route' in types:
                extracted['street_name'] = long_name
            elif 'locality' in types:
                extracted['city'] = long_name
            elif 'administrative_area_level_1' in types:
                extracted['state'] = short_name
                extracted['state_full'] = long_name
            elif 'postal_code' in types:
                extracted['zip_code'] = long_name
            elif 'country' in types:
                extracted['country'] = short_name
                extracted['country_full'] = long_name
        
        return extracted
    
    def standardize_address(self, address, components):
        """Standardize address format based on geocoding components"""
        if not components:
            return address
        
        # Build standardized address
        parts = []
        
        # Street number and name
        if 'street_number' in components and 'street_name' in components:
            parts.append(f"{components['street_number']} {components['street_name']}")
        elif 'street_name' in components:
            parts.append(components['street_name'])
        
        # City
        if 'city' in components:
            parts.append(components['city'])
        
        # State and ZIP
        if 'state' in components and 'zip_code' in components:
            parts.append(f"{components['state']} {components['zip_code']}")
        elif 'state' in components:
            parts.append(components['state'])
        
        return ', '.join(parts) if parts else address
    
    def get_center_from_address(self, address):
        """Determine center (CA, IN, TX, Other) from address"""
        if not self.gmaps:
            return 'Unknown'
        
        try:
            geocode_result = self.gmaps.geocode(address)
            if geocode_result:
                components = geocode_result[0].get('address_components', [])
                
                for component in components:
                    if 'administrative_area_level_1' in component.get('types', []):
                        state = component.get('short_name', '').upper()
                        
                        if state == 'CA':
                            return 'CA'
                        elif state == 'IN':
                            return 'IN'
                        elif state == 'TX':
                            return 'TX'
                        else:
                            return 'Other'
            
            return 'Unknown'
            
        except Exception as e:
            return 'Unknown'
    
    def batch_validate(self, addresses, batch_size=10):
        """Validate addresses in batches to respect rate limits"""
        results = []
        
        for i in range(0, len(addresses), batch_size):
            batch = addresses[i:i + batch_size]
            batch_results = []
            
            for address in batch:
                result = self.validate_single_address(address)
                batch_results.append(result)
                time.sleep(0.2)  # Rate limiting
            
            results.extend(batch_results)
            
            # Longer delay between batches
            if i + batch_size < len(addresses):
                time.sleep(1)
        
        return results
    
    def validate_single_address(self, address):
        """Validate a single address"""
        if not self.gmaps:
            return {'error': 'Google Maps API not configured'}
        
        try:
            geocode_result = self.gmaps.geocode(address)
            
            if geocode_result:
                first_result = geocode_result[0]
                return {
                    'is_valid': True,
                    'formatted_address': first_result['formatted_address'],
                    'confidence': self._calculate_confidence(first_result),
                    'components': self._extract_components(first_result.get('address_components', [])),
                    'coordinates': first_result.get('geometry', {}).get('location', {})
                }
            else:
                return {'is_valid': False, 'error': 'Address not found'}
                
        except Exception as e:
            return {'is_valid': False, 'error': f'Geocoding error: {str(e)}'}

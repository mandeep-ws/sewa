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
    
    def validate_addresses(self, df, progress_callback=None):
        """Validate addresses using Google Geocoding API"""
        if not self.gmaps:
            st.error("❌ Google Maps API not configured. Cannot validate addresses.")
            return pd.DataFrame()
        
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
                    # Geocode the address
                    geocode_result = self.gmaps.geocode(address)
                    
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
                    result['error'] = f'Geocoding error: {str(e)}'
            
            results.append(result)
            processed += 1
            
            # Add delay to respect API rate limits
            time.sleep(0.2)
        
        if progress_callback:
            progress_callback(min(processed, total_addresses), total_addresses)
        
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

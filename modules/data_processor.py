"""
Data processing module for handling SMS and Book data
"""

import pandas as pd
import streamlit as st
from pathlib import Path
import re

class DataProcessor:
    def __init__(self):
        pass
    
    def load_sms_data(self, uploaded_file):
        """Load and clean SMS data from uploaded file"""
        try:
            # Read the Excel file
            df = pd.read_excel(uploaded_file)
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            # Clean phone numbers
            if 'Phone' in df.columns:
                # Handle float phone numbers (like 2065044242.0) by converting to int first
                df['Phone'] = df['Phone'].apply(lambda x: str(int(x)) if pd.notna(x) and str(x) != 'nan' and str(x).replace('.0', '').isdigit() else '')
                # Remove any remaining non-digits
                df['Phone'] = df['Phone'].str.replace(r'[^\d]', '', regex=True)
                df['Phone'] = df['Phone'].str.replace('nan', '')
            
            # Clean addresses
            if 'Address' in df.columns:
                df['Address'] = df['Address'].astype(str).str.strip()
                df['Address'] = df['Address'].str.replace('nan', '')
            
            # Clean names
            if 'Name' in df.columns:
                df['Name'] = df['Name'].astype(str).str.strip()
                df['Name'] = df['Name'].str.replace('nan', '')
            
            # Clean book and language columns
            if 'Book' in df.columns:
                df['Book'] = df['Book'].astype(str).str.strip().str.upper()
                df['Book'] = df['Book'].str.replace('nan', '')
            
            if 'Language' in df.columns:
                df['Language'] = df['Language'].astype(str).str.strip().str.title()
                df['Language'] = df['Language'].str.replace('nan', '')
            
            # Filter out rows where both Name and Phone are empty
            if 'Name' in df.columns and 'Phone' in df.columns:
                # Keep only rows where both Name and Phone have valid values
                df = df[(df['Name'].str.strip() != '') & (df['Phone'].str.strip() != '')]
            
            return df
            
        except Exception as e:
            st.error(f"Error loading SMS data: {str(e)}")
            raise
    
    def load_book_data(self):
        """Load book data - now returns empty dataframe since we use All_Sent_Records.xlsx"""
        return pd.DataFrame()
    
    def standardize_address(self, address):
        """Standardize address format"""
        if pd.isna(address) or address == '' or address == 'nan':
            return ''
        
        # Basic cleaning
        address = str(address).strip()
        
        # Remove extra whitespace
        address = re.sub(r'\s+', ' ', address)
        
        # Basic format: Street, City, State Zip
        # This is a simple implementation - Google Geocoding will do the heavy lifting
        return address
    
    def standardize_phone(self, phone):
        """Standardize phone number format to 1xxxxxxxxx"""
        if pd.isna(phone) or phone == '' or phone == 'nan':
            return ''
        
        # Remove all non-digits
        phone = re.sub(r'[^\d]', '', str(phone))
        
        # Handle different formats
        if len(phone) == 10:
            # Add country code
            phone = '1' + phone
        elif len(phone) == 11 and phone.startswith('1'):
            # Already has country code
            pass
        elif len(phone) > 11:
            # Take last 11 digits
            phone = phone[-11:]
        
        return phone if len(phone) == 11 else ''
    
    def get_book_full_name(self, book_code, language=''):
        """Get full book name from code"""
        book_mapping = {
            'GG': 'Gyaan Ganga',
            'GTGA': 'Gita Tera Gyan Amrit',
            'JKR': 'Jeene ki Rah',
            'YBB': 'Yatharth Bhakti Bodh',
            'BSBT': 'Bhakti se bhagwan tak',
            'KP': 'Kabir parichay',
            'GGK': 'Garima Gitya ki',
            'HDM': 'Hindu Dharma Mahaan'
        }
        
        return book_mapping.get(book_code, book_code)
    
    def detect_center(self, address):
        """Detect center based on address (CA, IN, TX, other)"""
        if pd.isna(address) or address == '':
            return 'Unknown'
        
        address_upper = str(address).upper()
        
        if any(state in address_upper for state in ['CA', 'CALIFORNIA', 'CALIF']):
            return 'CA'
        elif any(state in address_upper for state in ['IN', 'INDIANA']):
            return 'IN'
        elif any(state in address_upper for state in ['TX', 'TEXAS']):
            return 'TX'
        else:
            return 'Other'


"""
Duplicate detection module for finding existing customers
"""

import pandas as pd
import streamlit as st
from difflib import SequenceMatcher
import re

class DuplicateDetector:
    def __init__(self):
        self.similarity_threshold = 0.8
    
    def find_duplicates(self, sms_data, book_data, progress_callback=None):
        """Find duplicates based on phone number and address"""
        if book_data.empty:
            st.warning("No historical book data available for duplicate detection")
            return pd.DataFrame()
        
        duplicates = []
        total_records = len(sms_data)
        processed = 0
        
        for idx, sms_row in sms_data.iterrows():
            if idx % 10 == 0 and progress_callback:
                progress_callback(min(processed, total_records), total_records)
            
            sms_phone = self._clean_phone(sms_row.get('Phone', ''))
            sms_address = self._clean_address(sms_row.get('Address', ''))
            
            if not sms_phone and not sms_address:
                continue
            
            # Find matches in book data
            phone_matches = []
            address_matches = []
            
            for book_idx, book_row in book_data.iterrows():
                book_phone = self._clean_phone(book_row.get('Phone', ''))
                book_address = self._clean_address(book_row.get('Address', ''))
                
                # Check phone match
                if sms_phone and book_phone and sms_phone == book_phone:
                    phone_matches.append({
                        'book_index': book_idx,
                        'match_type': 'phone',
                        'match_value': sms_phone,
                        'book_data': book_row.to_dict()
                    })
                
                # Check address match
                if sms_address and book_address:
                    similarity = self._calculate_address_similarity(sms_address, book_address)
                    if similarity >= self.similarity_threshold:
                        address_matches.append({
                            'book_index': book_idx,
                            'match_type': 'address',
                            'match_value': book_address,
                            'similarity': similarity,
                            'book_data': book_row.to_dict()
                        })
            
            # If we found matches, add to duplicates
            if phone_matches or address_matches:
                duplicate_record = {
                    'sms_index': idx,
                    'sms_name': sms_row.get('Name', ''),
                    'sms_phone': sms_phone,
                    'sms_address': sms_address,
                    'sms_book': sms_row.get('Book', ''),
                    'sms_language': sms_row.get('Language', ''),
                    'phone_matches': phone_matches,
                    'address_matches': address_matches,
                    'total_matches': len(phone_matches) + len(address_matches),
                    'is_duplicate': True
                }
                duplicates.append(duplicate_record)
            
            processed += 1
        
        if progress_callback:
            progress_callback(min(processed, total_records), total_records)
        
        return pd.DataFrame(duplicates)
    
    def _clean_phone(self, phone):
        """Clean and standardize phone number"""
        if pd.isna(phone) or phone == '' or phone == 'nan':
            return ''
        
        # Remove all non-digits
        phone = re.sub(r'[^\d]', '', str(phone))
        
        # Standardize to 11 digits with country code
        if len(phone) == 10:
            phone = '1' + phone
        elif len(phone) == 11 and phone.startswith('1'):
            pass
        elif len(phone) > 11:
            phone = phone[-11:]
        else:
            return ''
        
        return phone if len(phone) == 11 else ''
    
    def _clean_address(self, address):
        """Clean and standardize address"""
        if pd.isna(address) or address == '' or address == 'nan':
            return ''
        
        # Convert to lowercase and remove extra spaces
        address = str(address).lower().strip()
        address = re.sub(r'\s+', ' ', address)
        
        # Remove common abbreviations and standardize
        replacements = {
            'street': 'st',
            'avenue': 'ave',
            'road': 'rd',
            'drive': 'dr',
            'lane': 'ln',
            'boulevard': 'blvd',
            'apartment': 'apt',
            'suite': 'ste',
            'unit': 'unit',
            'north': 'n',
            'south': 's',
            'east': 'e',
            'west': 'w',
            'northeast': 'ne',
            'northwest': 'nw',
            'southeast': 'se',
            'southwest': 'sw'
        }
        
        for full, abbrev in replacements.items():
            address = re.sub(r'\b' + full + r'\b', abbrev, address)
        
        return address
    
    def _calculate_address_similarity(self, address1, address2):
        """Calculate similarity between two addresses"""
        # Use SequenceMatcher for basic similarity
        similarity = SequenceMatcher(None, address1, address2).ratio()
        
        # Boost similarity if key components match
        addr1_parts = set(address1.split())
        addr2_parts = set(address2.split())
        
        # Check for common words (street numbers, names, etc.)
        common_words = addr1_parts.intersection(addr2_parts)
        if common_words:
            # Boost similarity based on common words
            word_boost = len(common_words) * 0.1
            similarity = min(similarity + word_boost, 1.0)
        
        return similarity
    
    def get_duplicate_summary(self, duplicates_df):
        """Get summary statistics of duplicates"""
        if duplicates_df.empty:
            return {
                'total_duplicates': 0,
                'phone_duplicates': 0,
                'address_duplicates': 0,
                'both_duplicates': 0
            }
        
        phone_duplicates = len(duplicates_df[duplicates_df['phone_matches'].apply(len) > 0])
        address_duplicates = len(duplicates_df[duplicates_df['address_matches'].apply(len) > 0])
        both_duplicates = len(duplicates_df[
            (duplicates_df['phone_matches'].apply(len) > 0) & 
            (duplicates_df['address_matches'].apply(len) > 0)
        ])
        
        return {
            'total_duplicates': len(duplicates_df),
            'phone_duplicates': phone_duplicates,
            'address_duplicates': address_duplicates,
            'both_duplicates': both_duplicates
        }
    
    def get_duplicate_message_template(self, duplicate_record):
        """Get the appropriate message template for duplicate customers"""
        # This corresponds to Column Z in your Book.xlsx
        phone_matches = duplicate_record.get('phone_matches', [])
        address_matches = duplicate_record.get('address_matches', [])
        
        # Get the most recent match
        all_matches = phone_matches + address_matches
        if not all_matches:
            return None
        
        # Sort by date if available
        most_recent_match = all_matches[0]
        book_record = most_recent_match['book_data']
        
        # Get book name and language
        book_code = book_record.get('Book', '')
        language = book_record.get('Language', '')
        
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
        
        # Generate message template
        message = f"""Hello, you requested a free book called *{book_name}* in {language} from Sant Rampal Ji Maharaj.

However our records indicate that we had already mailed you a free book in the past. Can you please confirm if you already received a book in the past?"""
        
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

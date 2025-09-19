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
    
    def find_duplicates(self, sms_data, book_data=None, progress_callback=None, use_multithreading=True, max_workers=10):
        """Find duplicates based on phone number and address using All_Sent_Records.xlsx only"""
        # Load historical data from All_Sent_Records.xlsx only (ignore book_data parameter)
        historical_data = self._load_all_sent_records()
        
        if historical_data.empty:
            st.warning("No historical records available for duplicate detection")
            return pd.DataFrame()
        
        if use_multithreading:
            return self._find_duplicates_multithreaded(sms_data, historical_data, progress_callback, max_workers)
        else:
            return self._find_duplicates_sequential(sms_data, historical_data, progress_callback)
    
    def _find_duplicates_sequential(self, sms_data, historical_data, progress_callback=None):
        """Original sequential duplicate detection"""
        duplicates = []
        total_records = len(sms_data)
        processed = 0
        
        for idx, sms_row in sms_data.iterrows():
            if idx % 10 == 0 and progress_callback:
                progress_callback(min(processed, total_records), total_records)
            
            sms_phone = self._clean_phone(sms_row.get('Phone', ''))
            sms_address = self._clean_address(sms_row.get('Address', ''))
            sms_name = str(sms_row.get('Name', '')).strip().lower()
            
            if not sms_phone and not sms_address:
                continue
            
            # Find matches in historical data
            phone_matches = []
            address_matches = []
            
            for hist_idx, hist_row in historical_data.iterrows():
                hist_phone = self._clean_phone(hist_row.get('Phone', ''))
                hist_address = self._clean_address(hist_row.get('Address', ''))
                hist_name = str(hist_row.get('Name', '')).strip().lower()
                
                # Check phone match (must match both phone AND name for phone-based duplicates)
                if sms_phone and hist_phone and sms_phone == hist_phone and sms_name and hist_name and sms_name == hist_name:
                    phone_matches.append({
                        'historical_index': hist_idx,
                        'match_type': 'phone',
                        'match_value': sms_phone,
                        'historical_data': hist_row.to_dict()
                    })
                
                # Check address match
                if sms_address and hist_address:
                    similarity = self._calculate_address_similarity(sms_address, hist_address)
                    if similarity >= self.similarity_threshold:
                        address_matches.append({
                            'historical_index': hist_idx,
                            'match_type': 'address',
                            'match_value': hist_address,
                            'similarity': similarity,
                            'historical_data': hist_row.to_dict()
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
    
    def _find_duplicates_multithreaded(self, sms_data, historical_data, progress_callback=None, max_workers=10):
        """Multithreaded duplicate detection for better performance"""
        import concurrent.futures
        import threading
        
        # Only use multithreading for larger datasets to avoid overhead
        if len(sms_data) < 10:
            return self._find_duplicates_sequential(sms_data, historical_data, progress_callback)
        
        # Prepare data for multithreading - chunk the data for better performance
        chunk_size = max(1, len(sms_data) // max_workers)
        sms_chunks = []
        
        for i in range(0, len(sms_data), chunk_size):
            chunk = sms_data.iloc[i:i+chunk_size]
            sms_chunks.append(chunk)
        
        total_records = len(sms_data)
        
        # Thread-safe progress tracking
        progress_lock = threading.Lock()
        processed_count = 0
        duplicates = []
        
        def find_duplicates_for_chunk(chunk_data):
            nonlocal processed_count
            chunk_duplicates = []
            
            for idx, sms_row in chunk_data.iterrows():
                sms_phone = self._clean_phone(sms_row.get('Phone', ''))
                sms_address = self._clean_address(sms_row.get('Address', ''))
                sms_name = str(sms_row.get('Name', '')).strip().lower()
                
                if not sms_phone and not sms_address:
                    continue
                
                # Find matches in historical data
                phone_matches = []
                address_matches = []
                
                for hist_idx, hist_row in historical_data.iterrows():
                    hist_phone = self._clean_phone(hist_row.get('Phone', ''))
                    hist_address = self._clean_address(hist_row.get('Address', ''))
                    hist_name = str(hist_row.get('Name', '')).strip().lower()
                    
                    # Check phone match (must match both phone AND name for phone-based duplicates)
                    if sms_phone and hist_phone and sms_phone == hist_phone and sms_name and hist_name and sms_name == hist_name:
                        phone_matches.append({
                            'historical_index': hist_idx,
                            'match_type': 'phone',
                            'match_value': sms_phone,
                            'historical_data': hist_row.to_dict()
                        })
                    
                    # Check address match
                    if sms_address and hist_address:
                        similarity = self._calculate_address_similarity(sms_address, hist_address)
                        if similarity >= self.similarity_threshold:
                            address_matches.append({
                                'historical_index': hist_idx,
                                'match_type': 'address',
                                'match_value': hist_address,
                                'similarity': similarity,
                                'historical_data': hist_row.to_dict()
                            })
                
                # If we found matches, create duplicate record
                if phone_matches or address_matches:
                    duplicate_record = {
                        'sms_index': idx,
                        'sms_name': sms_row.get('Name', ''),
                        'sms_phone': sms_phone,
                        'sms_address': sms_address,
                        'sms_book': sms_row.get('Book', ''),
                        'sms_language': sms_row.get('Language', ''),
                        'phone_matches': phone_matches,
                        'address_matches': address_matches
                    }
                    chunk_duplicates.append(duplicate_record)
                
                # Update progress thread-safely
                with progress_lock:
                    processed_count += 1
                    if progress_callback and processed_count % 10 == 0:  # Update every 10 records
                        progress_callback(min(processed_count, total_records), total_records)
            
            return chunk_duplicates
        
        # Execute with ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all chunks
            future_to_chunk = {executor.submit(find_duplicates_for_chunk, chunk): chunk for chunk in sms_chunks}
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_chunk):
                try:
                    chunk_results = future.result()
                    duplicates.extend(chunk_results)
                except Exception as e:
                    # Handle any exceptions from individual chunk processing
                    chunk = future_to_chunk[future]
                    print(f"Error processing chunk: {e}")
        
        # Final progress update
        if progress_callback:
            progress_callback(total_records, total_records)
        
        return pd.DataFrame(duplicates)
    
    def _load_all_sent_records(self):
        """Load historical data from All_Sent_Records.xlsx"""
        try:
            import os
            historical_file = "All_Sent_Records.xlsx"
            if os.path.exists(historical_file):
                df = pd.read_excel(historical_file)
                # Filter out rows with empty names or phones for better matching
                df = df.dropna(subset=['Name', 'Phone'], how='all')
                return df
            else:
                return pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading historical records: {str(e)}")
            return pd.DataFrame()
    
    def _clean_phone(self, phone):
        """Clean and standardize phone number"""
        if pd.isna(phone) or phone == '' or phone == 'nan':
            return ''
        
        # Convert to string and handle float phone numbers (like 2065044242.0)
        phone_str = str(phone)
        
        # Handle float phone numbers by converting to int first
        try:
            if '.' in phone_str:
                phone_str = str(int(float(phone_str)))
        except (ValueError, TypeError):
            pass
        
        # Remove all non-digits
        phone = re.sub(r'[^\d]', '', phone_str)
        
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
    
    def _parse_address_components(self, address):
        """Parse address into structured components"""
        if not address:
            return {}
        
        # Clean the address first
        clean_addr = self._clean_address(address)
        parts = clean_addr.split()
        
        components = {
            'street_number': '',
            'street_name': '',
            'street_type': '',
            'city': '',
            'state': '',
            'zip_code': '',
            'full_street': '',
            'full_address': clean_addr
        }
        
        if not parts:
            return components
        
        # Extract zip code (last part if it's 5 digits)
        if parts and re.match(r'^\d{5}$', parts[-1]):
            components['zip_code'] = parts[-1]
            parts = parts[:-1]
        
        # Extract state (last part if it's 2 letters or common state names)
        state_patterns = [
            r'^(ca|tx|ny|fl|wa|il|nj|pa|ga|nc|va|oh|mi|az|tn|in|ma|md|co|or|ut|nv|ct|wi|mn|mo|la|al|sc|ky|ok|ia|ar|ks|nm|ne|wv|id|hi|nh|me|ri|mt|de|sd|nd|ak|vt|wy)$',
            r'^(california|texas|new york|florida|washington|illinois|new jersey|pennsylvania|georgia|north carolina|virginia|ohio|michigan|arizona|tennessee|indiana|massachusetts|maryland|colorado|oregon|utah|nevada|connecticut|wisconsin|minnesota|missouri|louisiana|alabama|south carolina|kentucky|oklahoma|iowa|arkansas|kansas|new mexico|nebraska|west virginia|idaho|hawaii|new hampshire|maine|rhode island|montana|delaware|south dakota|north dakota|alaska|vermont|wyoming)$'
        ]
        
        if parts:
            last_part = parts[-1]
            for pattern in state_patterns:
                if re.match(pattern, last_part):
                    components['state'] = last_part
                    parts = parts[:-1]
                    break
        
        # Extract city (everything between street and state)
        if parts:
            # Find where street ends and city begins
            # Look for common street types (these are the cleaned/abbreviated versions)
            street_types = ['st', 'ave', 'rd', 'dr', 'ln', 'blvd', 'ct', 'pl', 'way', 'cir', 'pkwy', 'tr']
            
            street_end_idx = 0
            for i, part in enumerate(parts):
                if part in street_types:
                    street_end_idx = i + 1
                    break
            
            # Extract street components
            if street_end_idx > 0:
                street_parts = parts[:street_end_idx]
                if street_parts:
                    # First part is usually street number
                    if re.match(r'^\d+$', street_parts[0]):
                        components['street_number'] = street_parts[0]
                        if len(street_parts) > 1:
                            # Last part is street type if it's in our list
                            if street_parts[-1] in street_types:
                                components['street_type'] = street_parts[-1]
                                components['street_name'] = ' '.join(street_parts[1:-1])
                            else:
                                components['street_name'] = ' '.join(street_parts[1:])
                    else:
                        # No street number, everything is street name/type
                        if street_parts[-1] in street_types:
                            components['street_type'] = street_parts[-1]
                            components['street_name'] = ' '.join(street_parts[:-1])
                        else:
                            components['street_name'] = ' '.join(street_parts)
                
                components['full_street'] = ' '.join(street_parts)
                
                # Extract city (remaining parts)
                if street_end_idx < len(parts):
                    components['city'] = ' '.join(parts[street_end_idx:])
            else:
                # No street type found, try to parse differently
                if parts and re.match(r'^\d+$', parts[0]):
                    components['street_number'] = parts[0]
                    # Try to find street type in remaining parts
                    remaining_parts = parts[1:]
                    for i, part in enumerate(remaining_parts):
                        if part in street_types:
                            components['street_type'] = part
                            components['street_name'] = ' '.join(remaining_parts[:i])
                            components['city'] = ' '.join(remaining_parts[i+1:])
                            break
                    else:
                        # No street type found, assume everything after number is street name
                        components['street_name'] = ' '.join(remaining_parts)
                else:
                    # No street number, try to find street type
                    for i, part in enumerate(parts):
                        if part in street_types:
                            components['street_type'] = part
                            components['street_name'] = ' '.join(parts[:i])
                            components['city'] = ' '.join(parts[i+1:])
                            break
                    else:
                        # No street type found, assume everything is street name
                        components['street_name'] = ' '.join(parts)
        
        return components
    
    def _calculate_address_similarity(self, address1, address2):
        """Calculate similarity between two addresses using weighted component matching"""
        # Parse both addresses into components
        comp1 = self._parse_address_components(address1)
        comp2 = self._parse_address_components(address2)
        
        # If either address couldn't be parsed, fall back to basic similarity
        if not comp1 or not comp2:
            return SequenceMatcher(None, address1, address2).ratio()
        
        # Component weights (must sum to 1.0)
        weights = {
            'street_number': 0.25,    # Street number is critical
            'street_name': 0.35,      # Street name is most important
            'street_type': 0.05,      # Street type is less important
            'city': 0.20,            # City is important
            'state': 0.10,           # State is moderately important
            'zip_code': 0.05         # Zip code is least important
        }
        
        total_score = 0.0
        component_scores = {}
        
        # Calculate similarity for each component
        for component, weight in weights.items():
            val1 = comp1.get(component, '').strip()
            val2 = comp2.get(component, '').strip()
            
            if not val1 and not val2:
                # Both empty - neutral score
                score = 0.5
            elif not val1 or not val2:
                # One empty - low score
                score = 0.0
            elif val1 == val2:
                # Exact match
                score = 1.0
            else:
                # Check for fuzzy matches
                if component == 'street_type':
                    # Street type variations (St vs Street)
                    score = self._fuzzy_match_street_type(val1, val2)
                elif component == 'state':
                    # State variations (CA vs California)
                    score = self._fuzzy_match_state(val1, val2)
                elif component == 'street_name':
                    # Street name fuzzy matching
                    score = self._fuzzy_match_street_name(val1, val2)
                else:
                    # For other components, use exact matching
                    score = 0.0
            
            component_scores[component] = score
            total_score += score * weight
        
        # Apply strict rules for critical components
        # If street number or street name don't match, significantly reduce score
        if (comp1.get('street_number') and comp2.get('street_number') and 
            comp1['street_number'] != comp2['street_number']):
            total_score *= 0.3  # Heavy penalty for different street numbers
        
        if (comp1.get('street_name') and comp2.get('street_name') and 
            component_scores['street_name'] < 0.8):
            total_score *= 0.5  # Penalty for different street names
        
        # If cities are different, reduce score significantly
        if (comp1.get('city') and comp2.get('city') and 
            comp1['city'] != comp2['city']):
            total_score *= 0.4  # Heavy penalty for different cities
        
        return min(total_score, 1.0)
    
    def _fuzzy_match_street_type(self, type1, type2):
        """Fuzzy match street types (St vs Street, Ave vs Avenue, etc.)"""
        street_type_mappings = {
            'st': ['street', 'st'],
            'ave': ['avenue', 'ave'],
            'rd': ['road', 'rd'],
            'dr': ['drive', 'dr'],
            'ln': ['lane', 'ln'],
            'blvd': ['boulevard', 'blvd'],
            'ct': ['court', 'ct'],
            'pl': ['place', 'pl'],
            'way': ['way'],
            'cir': ['circle', 'cir'],
            'pkwy': ['parkway', 'pkwy'],
            'tr': ['trail', 'tr']
        }
        
        # Normalize both types
        type1_norm = type1.lower().strip()
        type2_norm = type2.lower().strip()
        
        # Check if they're in the same group
        for group in street_type_mappings.values():
            if type1_norm in group and type2_norm in group:
                return 1.0
        
        # If not in same group, check similarity
        return SequenceMatcher(None, type1_norm, type2_norm).ratio()
    
    def _fuzzy_match_state(self, state1, state2):
        """Fuzzy match states (CA vs California, etc.)"""
        state_mappings = {
            'ca': 'california',
            'tx': 'texas',
            'ny': 'new york',
            'fl': 'florida',
            'wa': 'washington',
            'il': 'illinois',
            'nj': 'new jersey',
            'pa': 'pennsylvania',
            'ga': 'georgia',
            'nc': 'north carolina',
            'va': 'virginia',
            'oh': 'ohio',
            'mi': 'michigan',
            'az': 'arizona',
            'tn': 'tennessee',
            'in': 'indiana',
            'ma': 'massachusetts',
            'md': 'maryland',
            'co': 'colorado',
            'or': 'oregon',
            'ut': 'utah',
            'nv': 'nevada',
            'ct': 'connecticut',
            'wi': 'wisconsin',
            'mn': 'minnesota',
            'mo': 'missouri',
            'la': 'louisiana',
            'al': 'alabama',
            'sc': 'south carolina',
            'ky': 'kentucky',
            'ok': 'oklahoma',
            'ia': 'iowa',
            'ar': 'arkansas',
            'ks': 'kansas',
            'nm': 'new mexico',
            'ne': 'nebraska',
            'wv': 'west virginia',
            'id': 'idaho',
            'hi': 'hawaii',
            'nh': 'new hampshire',
            'me': 'maine',
            'ri': 'rhode island',
            'mt': 'montana',
            'de': 'delaware',
            'sd': 'south dakota',
            'nd': 'north dakota',
            'ak': 'alaska',
            'vt': 'vermont',
            'wy': 'wyoming'
        }
        
        state1_norm = state1.lower().strip()
        state2_norm = state2.lower().strip()
        
        # Check if they're the same state in different formats
        if state1_norm in state_mappings and state_mappings[state1_norm] == state2_norm:
            return 1.0
        if state2_norm in state_mappings and state_mappings[state2_norm] == state1_norm:
            return 1.0
        if state1_norm == state2_norm:
            return 1.0
        
        return 0.0
    
    def _fuzzy_match_street_name(self, name1, name2):
        """Fuzzy match street names with some tolerance for minor differences"""
        name1_norm = name1.lower().strip()
        name2_norm = name2.lower().strip()
        
        # Exact match
        if name1_norm == name2_norm:
            return 1.0
        
        # Check for common variations
        variations = {
            'north': 'n',
            'south': 's',
            'east': 'e',
            'west': 'w',
            'northeast': 'ne',
            'northwest': 'nw',
            'southeast': 'se',
            'southwest': 'sw'
        }
        
        # Try with variations
        for full, abbrev in variations.items():
            name1_variation = name1_norm.replace(full, abbrev).replace(abbrev, full)
            name2_variation = name2_norm.replace(full, abbrev).replace(abbrev, full)
            
            if name1_variation == name2_norm or name1_norm == name2_variation:
                return 0.9
        
        # Use sequence matcher for fuzzy matching
        similarity = SequenceMatcher(None, name1_norm, name2_norm).ratio()
        
        # Only accept high similarity for street names
        return similarity if similarity >= 0.8 else 0.0
    
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
        print(f"🔍 DEBUG: get_duplicate_message_template function called with duplicate_record: {duplicate_record}")
        logger.info(f"🔍 DEBUG: get_duplicate_message_template function called with duplicate_record: {duplicate_record}")
        # This corresponds to the duplicate message template
        phone_matches = duplicate_record.get('phone_matches', [])
        address_matches = duplicate_record.get('address_matches', [])
        print(f"🔍 DEBUG: phone_matches: {len(phone_matches)}, address_matches: {len(address_matches)}")
        logger.info(f"🔍 DEBUG: phone_matches: {len(phone_matches)}, address_matches: {len(address_matches)}")
        
        # Get the most recent match
        all_matches = phone_matches + address_matches
        if not all_matches:
            return None
        
        # Sort by date if available to get the most recent match
        from datetime import datetime
        def get_sent_date(match):
            historical_data = match.get('historical_data', {})
            sent_date = historical_data.get('Sent_Date', '')
            logger.info(f"🔍 DEBUG: Processing match with sent_date: {sent_date}")
            if sent_date:
                try:
                    # Handle different date formats
                    if isinstance(sent_date, datetime):
                        return sent_date
                    elif isinstance(sent_date, str):
                        return datetime.strptime(str(sent_date), '%Y-%m-%d %H:%M:%S')
                    else:
                        return datetime.min
                except Exception as e:
                    logger.error(f"🔍 DEBUG: Error parsing date {sent_date}: {e}")
                    return datetime.min
            return datetime.min
        
        # Sort by date (most recent first)
        all_matches.sort(key=get_sent_date, reverse=True)
        most_recent_match = all_matches[0]
        historical_record = most_recent_match['historical_data']
        
        # Debug logging to see what historical record is being used
        logger.info(f"🔍 DEBUG: Found {len(all_matches)} historical matches")
        for i, match in enumerate(all_matches):
            hist_data = match.get('historical_data', {})
            logger.info(f"🔍 DEBUG: Match {i}: Book={hist_data.get('Book', 'N/A')}, Date={hist_data.get('Sent_Date', 'N/A')}")
        logger.info(f"🔍 DEBUG: Using most recent match: Book={historical_record.get('Book', 'N/A')}, Date={historical_record.get('Sent_Date', 'N/A')}")
        
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

#!/usr/bin/env python3
"""
Main Streamlit application for Book Request Automation System
"""

import streamlit as st
import pandas as pd
import os
import logging
from pathlib import Path
from streamlit_option_menu import option_menu
from dotenv import load_dotenv

# Load environment variables from config.env
load_dotenv('config.env')

# Set up logging
logger = logging.getLogger(__name__)

# Import our custom modules
from modules.data_processor import DataProcessor
from modules.phone_validator import PhoneValidator
from modules.address_validator import AddressValidator
from modules.duplicate_detector import DuplicateDetector
from modules.message_sender import MessageSender
from modules.ui_components import UIComponents

# Create instances of the classes
duplicate_detector = DuplicateDetector()

# Page configuration
st.set_page_config(
    page_title="Book Request Automation",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    try:
        # Initialize session state
        if 'sms_data' not in st.session_state:
            st.session_state.sms_data = None
        if 'processed_data' not in st.session_state:
            st.session_state.processed_data = None
        if 'duplicates' not in st.session_state:
            st.session_state.duplicates = None
        if 'validation_results' not in st.session_state:
            st.session_state.validation_results = {}

        # Main header
        st.markdown('<h1 class="main-header">📚 Book Request Automation System</h1>', unsafe_allow_html=True)
        
        # Sidebar navigation
        with st.sidebar:
            st.image("https://via.placeholder.com/200x100/1f77b4/ffffff?text=SEWA", width=200)
            
            selected = option_menu(
                menu_title="Navigation",
                options=["📁 Upload Data", "🔍 Validate Data", "📱 Send Messages", "📊 Analytics"],
                icons=["upload", "search", "send", "graph-up"],
                menu_icon="cast",
                default_index=0,
            )
        
        # Initialize components
        data_processor = DataProcessor()
        phone_validator = PhoneValidator()
        address_validator = AddressValidator()
        duplicate_detector = DuplicateDetector()
        message_sender = MessageSender()
        ui_components = UIComponents()

        # Route to different pages
        if selected == "📁 Upload Data":
            upload_data_page(data_processor, ui_components)
        elif selected == "🔍 Validate Data":
            validate_data_page(phone_validator, address_validator, duplicate_detector, ui_components)
        elif selected == "📱 Send Messages":
            send_messages_page(message_sender, ui_components)
        elif selected == "📊 Analytics":
            analytics_page(ui_components)
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please refresh the page and try again.")
        st.exception(e)

def upload_data_page(data_processor, ui_components):
    """Handle file upload and initial data processing"""
    st.markdown('<h2 class="section-header">📁 Upload SMS Data</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File upload
        uploaded_file = st.file_uploader(
            "Upload SMS.xlsx file",
            type=['xlsx'],
            help="Upload the weekly SMS data file"
        )
        
        if uploaded_file is not None:
            try:
                # Process the uploaded file
                with st.spinner("Processing uploaded file..."):
                    sms_data = data_processor.load_sms_data(uploaded_file)
                    st.session_state.sms_data = sms_data
                
                st.success(f"✅ Successfully loaded {len(sms_data)} records from SMS file")
                
                # Show data preview
                ui_components.show_data_preview(sms_data, "SMS Data Preview")
                
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
    
    with col2:
        st.markdown("### 📋 Instructions")
        st.markdown("""
        1. **Upload SMS.xlsx** - Your weekly data file
        2. **Review Data** - Check the preview below
        3. **Validate** - Go to Validate Data tab
        4. **Send Messages** - Process and send communications
        """)
        
        # Show current status
        if st.session_state.sms_data is not None:
            st.markdown("### 📊 Current Status")
            st.metric("SMS Records", len(st.session_state.sms_data))
            
            # Data quality indicators
            sms_data = st.session_state.sms_data
            missing_books = sms_data['Book'].isna().sum()
            missing_languages = sms_data['Language'].isna().sum()
            
            st.metric("Missing Books", missing_books)
            st.metric("Missing Languages", missing_languages)

def validate_data_page(phone_validator, address_validator, duplicate_detector, ui_components):
    """Handle data validation and duplicate detection"""
    st.markdown('<h2 class="section-header">🔍 Validate & Process Data</h2>', unsafe_allow_html=True)
    
    if st.session_state.sms_data is None:
        st.warning("⚠️ Please upload SMS data first in the Upload Data tab")
        return
    
    
    # Performance settings
    st.markdown("#### ⚡ Performance Settings")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        use_multithreading = st.checkbox("Enable Multithreading", value=True, help="Use multiple threads for faster processing")
    
    with col2:
        max_workers = st.slider("Max Workers", min_value=1, max_value=20, value=10, help="Number of parallel threads to use")
    
    with col3:
        api_delay = st.slider("API Delay (seconds)", min_value=0.1, max_value=2.0, value=0.5, step=0.1, help="Delay between API calls to avoid rate limiting")
    
    st.info(f"💡 **Tip**: Multithreading can be 5-10x faster for large datasets. Increase API delay if you get rate limit errors.")
    
    # Show current settings
    st.caption(f"⚙️ **Current Settings**: Multithreading: {'ON' if use_multithreading else 'OFF'}, Workers: {max_workers}, API Delay: {api_delay}s")
    
    # Validation options
    st.markdown("#### 🔍 Validation Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        validate_phones = st.button("📞 Validate Phone Numbers", type="primary")
    
    with col2:
        validate_addresses = st.button("🏠 Validate Addresses", type="primary")
    
    with col3:
        check_duplicates = st.button("🔄 Check Duplicates", type="primary")
    
    # Add a button to clear duplicate detection results
    if st.button("🗑️ Clear Duplicate Results", help="Clear existing duplicate detection results to force a fresh run"):
        st.session_state.duplicates = None
        st.success("✅ Duplicate detection results cleared!")
        st.rerun()
    
    # Phone validation
    if validate_phones:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(current, total):
            progress = min(current / total, 1.0)  # Ensure progress never exceeds 1.0
            progress_bar.progress(progress)
            status_text.text(f"Validating {current}/{total} phone numbers...")
        
        validation_results = phone_validator.validate_phones(
            st.session_state.sms_data,
            progress_callback=update_progress,
            use_multithreading=use_multithreading,
            max_workers=max_workers
        )
        progress_bar.progress(1.0)
        status_text.text("✅ Phone validation completed!")
        
        if 'validation_results' not in st.session_state:
            st.session_state.validation_results = {}
        st.session_state.validation_results['phones'] = validation_results
        
        # Auto-export phone validation results
        ui_components._export_validation_results_to_excel(
            validation_results, 
            "phone_validation", 
            "Phone_Validation_Results"
        )
        
        ui_components.show_phone_validation_results(validation_results)
    
    # Address validation
    if validate_addresses:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(current, total):
            progress = min(current / total, 1.0)  # Ensure progress never exceeds 1.0
            progress_bar.progress(progress)
            status_text.text(f"Validating {current}/{total} addresses...")
        
        address_results = address_validator.validate_addresses(
            st.session_state.sms_data,
            progress_callback=update_progress,
            use_multithreading=use_multithreading,
            max_workers=max_workers,
            api_delay=api_delay
        )
        progress_bar.progress(1.0)
        status_text.text("✅ Address validation completed!")
        
        if 'validation_results' not in st.session_state:
            st.session_state.validation_results = {}
        st.session_state.validation_results['addresses'] = address_results
        
        # Auto-export address validation results
        ui_components._export_validation_results_to_excel(
            address_results, 
            "address_validation", 
            "Address_Validation_Results"
        )
        
        ui_components.show_address_validation_results(address_results)
    
    # Duplicate detection
    if check_duplicates:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(current, total):
            progress = min(current / total, 1.0)  # Ensure progress never exceeds 1.0
            progress_bar.progress(progress)
            status_text.text(f"Checking {current}/{total} records for duplicates...")
        
        duplicates = duplicate_detector.find_duplicates(
            st.session_state.sms_data, 
            progress_callback=update_progress,
            use_multithreading=use_multithreading,
            max_workers=max_workers
        )
        progress_bar.progress(1.0)
        status_text.text("✅ Duplicate detection completed!")
        
        st.session_state.duplicates = duplicates
        
        # Auto-export duplicate detection results
        ui_components._export_validation_results_to_excel(
            duplicates, 
            "duplicate_detection", 
            "Duplicate_Detection_Results"
        )
        
        ui_components.show_duplicate_results(duplicates)
    
    # Show validation results if available
    if st.session_state.validation_results and len(st.session_state.validation_results) > 0:
        ui_components.show_validation_summary(st.session_state.validation_results)
    

def send_messages_page(message_sender, ui_components):
    """Handle message sending functionality"""
    st.markdown('<h2 class="section-header">📱 Send Messages</h2>', unsafe_allow_html=True)
    
    if st.session_state.sms_data is None:
        st.warning("⚠️ Please upload and validate data first")
        return
    
    # Performance settings for message sending
    st.markdown("#### ⚡ Message Sending Performance")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        use_multithreading_messages = st.checkbox("Enable Multithreading for Messages", value=True, help="Use multiple threads for faster message sending")
    
    with col2:
        max_workers_messages = st.slider("Max Workers for Messages", min_value=1, max_value=10, value=5, help="Number of parallel threads for message sending")
    
    with col3:
        st.info(f"💡 **Tip**: Multithreading can significantly speed up message sending")
    
    # Message sending options
    st.markdown("#### 📤 Message Sending Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        send_whatsapp = st.button("💬 Send WhatsApp Only", type="primary")
    
    with col2:
        send_sms = st.button("📱 Send SMS Only", type="primary")
    
    with col3:
        send_both = st.button("🔄 Send Both", type="primary")
    
    # Show pending messages
    if st.session_state.processed_data is not None:
        ui_components.show_pending_messages(st.session_state.processed_data)
    
    # Message sending logic
    if send_whatsapp or send_sms or send_both:
        logger.info(f"🔘 Send messages button clicked! WhatsApp: {send_whatsapp}, SMS: {send_sms}, Both: {send_both}")
        logger.info(f"📊 SMS data available: {st.session_state.sms_data is not None}")
        logger.info(f"📊 Duplicates available: {st.session_state.duplicates is not None}")
        
        # Handle SMS sending directly
        if send_sms:
            logger.info("🔘 SMS button clicked - running duplicate detection first")
            st.success("🚀 Starting duplicate detection...")
            
            # Always run duplicate detection to ensure we have current results
            logger.info("📊 Running duplicate detection before sending SMS...")
            
            # Create progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(current, total):
                progress = min(current / total, 1.0)
                progress_bar.progress(progress)
                status_text.text(f"Checking {current}/{total} records for duplicates...")
            
            # Run duplicate detection
            duplicates = duplicate_detector.find_duplicates(
                st.session_state.sms_data, 
                progress_callback=update_progress,
                use_multithreading=use_multithreading,
                max_workers=max_workers
            )
            progress_bar.progress(1.0)
            status_text.text("✅ Duplicate detection completed!")
            
            # Store duplicates in session state
            st.session_state.duplicates = duplicates
            logger.info(f"📊 Duplicate detection completed: {len(duplicates) if duplicates is not None else 0} duplicates found")
            
            st.success("🚀 Starting SMS sending...")
            try:
                ui_components._send_sms_messages(
                    st.session_state.sms_data,
                    st.session_state.duplicates,
                    message_sender,
                    use_multithreading=use_multithreading_messages,
                    max_workers=max_workers_messages
                )
                logger.info("✅ SMS sending completed successfully")
            except Exception as e:
                logger.error(f"❌ Error sending SMS messages: {e}")
                st.error(f"Error sending messages: {e}")
        else:
            # For WhatsApp or Both options, run duplicate detection and send directly
            logger.info("📊 Running duplicate detection before sending messages...")
            st.success("🚀 Starting duplicate detection...")
            
            # Create progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(current, total):
                progress = min(current / total, 1.0)
                progress_bar.progress(progress)
                status_text.text(f"Checking {current}/{total} records for duplicates...")
            
            # Run duplicate detection
            duplicates = duplicate_detector.find_duplicates(
                st.session_state.sms_data, 
                progress_callback=update_progress,
                use_multithreading=use_multithreading,
                max_workers=max_workers
            )
            progress_bar.progress(1.0)
            status_text.text("✅ Duplicate detection completed!")
            
            # Store duplicates in session state
            st.session_state.duplicates = duplicates
            logger.info(f"📊 Duplicate detection completed: {len(duplicates) if duplicates is not None else 0} duplicates found")
            
            # Handle WhatsApp sending directly
            if send_whatsapp:
                logger.info("🔘 WhatsApp button clicked - sending directly")
                st.success("🚀 Starting WhatsApp sending...")
                try:
                    ui_components._send_whatsapp_messages(
                        st.session_state.sms_data,
                        st.session_state.duplicates,
                        message_sender,
                        use_multithreading=use_multithreading_messages,
                        max_workers=max_workers_messages
                    )
                    logger.info("✅ WhatsApp sending completed successfully")
                except Exception as e:
                    logger.error(f"❌ Error sending WhatsApp messages: {e}")
                    st.error(f"Error sending WhatsApp messages: {e}")
            
            # Handle Both sending directly
            if send_both:
                logger.info("🔘 Both button clicked - sending both SMS and WhatsApp directly")
                st.success("🚀 Starting Both SMS and WhatsApp sending...")
                try:
                    ui_components._send_both_messages(
                        st.session_state.sms_data,
                        st.session_state.duplicates,
                        message_sender,
                        use_multithreading=use_multithreading_messages,
                        max_workers=max_workers_messages
                    )
                    logger.info("✅ Both SMS and WhatsApp sending completed successfully")
                except Exception as e:
                    logger.error(f"❌ Error sending both messages: {e}")
                    st.error(f"Error sending both messages: {e}")

def analytics_page(ui_components):
    """Show analytics and reports"""
    st.markdown('<h2 class="section-header">📊 Analytics & Reports</h2>', unsafe_allow_html=True)
    
    if st.session_state.sms_data is None:
        st.warning("⚠️ Please upload data first to see analytics")
        return
    
    ui_components.show_analytics(st.session_state.sms_data)

if __name__ == "__main__":
    main()

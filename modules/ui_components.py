"""
UI components module for displaying data and results
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import logging
from typing import Dict, List, Optional
import os

# Set up logging
logger = logging.getLogger(__name__)

class UIComponents:
    def __init__(self):
        pass
    
    def safe_display_dataframe(self, df, max_rows=10):
        """Safely display a DataFrame without PyArrow serialization issues"""
        try:
            # Convert all columns to strings to avoid any serialization issues
            display_df = df.head(max_rows).copy()
            for col in display_df.columns:
                display_df[col] = display_df[col].astype(str)
            
            # Use st.table which doesn't use PyArrow
            st.table(display_df)
            return True
        except Exception as e:
            st.error(f"Error displaying data: {str(e)}")
            # Fallback to simple text display
            st.write("Data preview (text format):")
            try:
                for idx, row in df.head(max_rows).iterrows():
                    # Convert all values to strings to avoid serialization issues
                    row_dict = {str(k): str(v) if pd.notna(v) else 'NaN' for k, v in row.items()}
                    st.write(f"Row {idx}: {row_dict}")
            except Exception as fallback_error:
                st.error(f"Fallback display also failed: {str(fallback_error)}")
                st.write("Raw data info:")
                st.write(f"Shape: {df.shape}")
                st.write(f"Columns: {list(df.columns)}")
            return False
    
    def show_data_preview(self, df, title):
        """Show a preview of the data"""
        st.markdown(f"### {title}")
        
        # Show basic statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", len(df))
        
        with col2:
            missing_books = df['Book'].isna().sum() if 'Book' in df.columns else 0
            st.metric("Missing Books", missing_books)
        
        with col3:
            missing_languages = df['Language'].isna().sum() if 'Language' in df.columns else 0
            st.metric("Missing Languages", missing_languages)
        
        with col4:
            missing_phones = df['Phone'].isna().sum() if 'Phone' in df.columns else 0
            st.metric("Missing Phones", missing_phones)
        
        # Show data preview using safe display method
        self.safe_display_dataframe(df, max_rows=10)
        
        # Show data types
        with st.expander("Data Types"):
            try:
                # Convert dtypes to string to avoid PyArrow issues
                dtypes_str = {str(k): str(v) for k, v in df.dtypes.items()}
                st.write(dtypes_str)
            except Exception as e:
                st.error(f"Error displaying data types: {str(e)}")
                st.write("Data types not available")
    
    def show_phone_validation_results(self, validation_results):
        """Display phone validation results"""
        st.markdown("### 📞 Phone Validation Results")
        
        if validation_results.empty:
            st.warning("No phone validation results to display")
            return
        
        # Summary statistics
        total_phones = len(validation_results)
        valid_phones = len(validation_results[validation_results['is_valid'] == True])
        invalid_phones = total_phones - valid_phones
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Phones", total_phones)
        
        with col2:
            st.metric("Valid Phones", valid_phones, delta=f"{valid_phones/total_phones*100:.1f}%")
        
        with col3:
            st.metric("Invalid Phones", invalid_phones, delta=f"{invalid_phones/total_phones*100:.1f}%")
        
        # Show carrier distribution
        if valid_phones > 0:
            valid_results = validation_results[validation_results['is_valid'] == True]
            
            # Carrier distribution
            if 'carrier' in valid_results.columns:
                carrier_counts = valid_results['carrier'].value_counts()
                if not carrier_counts.empty:
                    st.markdown("#### 📊 Carrier Distribution")
                    fig = px.pie(
                        values=carrier_counts.values,
                        names=carrier_counts.index,
                        title="Phone Carriers"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Line type distribution
            if 'line_type' in valid_results.columns:
                line_type_counts = valid_results['line_type'].value_counts()
                if not line_type_counts.empty:
                    st.markdown("#### 📱 Line Type Distribution")
                    fig = px.bar(
                        x=line_type_counts.index,
                        y=line_type_counts.values,
                        title="Phone Line Types"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Mobile vs Landline breakdown
            if 'is_mobile' in valid_results.columns and 'is_landline' in valid_results.columns:
                mobile_count = valid_results['is_mobile'].sum()
                landline_count = valid_results['is_landline'].sum()
                voip_count = valid_results.get('is_voip', pd.Series([False] * len(valid_results))).sum()
                
                st.markdown("#### 📊 Phone Type Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Mobile", mobile_count)
                with col2:
                    st.metric("Landline", landline_count)
                with col3:
                    st.metric("VoIP", voip_count)
        
        # Show detailed results
        with st.expander("📋 Detailed Phone Validation Results"):
            # Filter options
            filter_option = st.selectbox(
                "Filter results:",
                ["All", "Valid Only", "Invalid Only", "With Errors", "Mobile Only", "Landline Only", "VoIP Only"]
            )
            
            filtered_results = validation_results.copy()
            
            if filter_option == "Valid Only":
                filtered_results = filtered_results[filtered_results['is_valid'] == True]
            elif filter_option == "Invalid Only":
                filtered_results = filtered_results[filtered_results['is_valid'] == False]
            elif filter_option == "With Errors":
                filtered_results = filtered_results[filtered_results['error'] != '']
            elif filter_option == "Mobile Only":
                filtered_results = filtered_results[filtered_results.get('is_mobile', False) == True]
            elif filter_option == "Landline Only":
                filtered_results = filtered_results[filtered_results.get('is_landline', False) == True]
            elif filter_option == "VoIP Only":
                filtered_results = filtered_results[filtered_results.get('is_voip', False) == True]
            
            # Display enhanced carrier information
            display_columns = [
                'name', 'original_phone', 'formatted_phone', 'is_valid', 
                'carrier', 'carrier_type', 'line_type', 'location', 'timezone', 'error'
            ]
            
            # Only show columns that exist in the dataframe
            available_columns = [col for col in display_columns if col in filtered_results.columns]
            
            # Use safe display method
            self.safe_display_dataframe(filtered_results[available_columns], max_rows=50)
            
            # Show carrier type breakdown
            if not filtered_results.empty and 'carrier_type' in filtered_results.columns:
                st.markdown("#### 📊 Carrier Type Breakdown")
                carrier_type_counts = filtered_results['carrier_type'].value_counts()
                fig = px.pie(
                    values=carrier_type_counts.values,
                    names=carrier_type_counts.index,
                    title="Phone Number Types"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def show_address_validation_results(self, address_results):
        """Display address validation results"""
        st.markdown("### 🏠 Address Validation Results")
        
        if address_results.empty:
            st.warning("No address validation results to display")
            return
        
        # Summary statistics
        total_addresses = len(address_results)
        valid_addresses = len(address_results[address_results['is_valid'] == True])
        invalid_addresses = total_addresses - valid_addresses
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Addresses", total_addresses)
        
        with col2:
            st.metric("Valid Addresses", valid_addresses, delta=f"{valid_addresses/total_addresses*100:.1f}%")
        
        with col3:
            st.metric("Invalid Addresses", invalid_addresses, delta=f"{invalid_addresses/total_addresses*100:.1f}%")
        
        # Show confidence distribution
        if valid_addresses > 0:
            valid_results = address_results[address_results['is_valid'] == True]
            confidence_data = valid_results['confidence'].dropna()
            
            if not confidence_data.empty:
                st.markdown("#### 📊 Address Confidence Distribution")
                fig = px.histogram(
                    confidence_data,
                    nbins=20,
                    title="Address Validation Confidence Scores",
                    labels={'value': 'Confidence Score', 'count': 'Number of Addresses'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Show detailed results
        with st.expander("📋 Detailed Address Validation Results"):
            # Filter options
            filter_option = st.selectbox(
                "Filter results:",
                ["All", "Valid Only", "Invalid Only", "High Confidence (>80%)", "Low Confidence (<50%)"]
            )
            
            filtered_results = address_results.copy()
            
            if filter_option == "Valid Only":
                filtered_results = filtered_results[filtered_results['is_valid'] == True]
            elif filter_option == "Invalid Only":
                filtered_results = filtered_results[filtered_results['is_valid'] == False]
            elif filter_option == "High Confidence (>80%)":
                filtered_results = filtered_results[
                    (filtered_results['is_valid'] == True) & 
                    (filtered_results['confidence'] > 80)
                ]
            elif filter_option == "Low Confidence (<50%)":
                filtered_results = filtered_results[
                    (filtered_results['is_valid'] == True) & 
                    (filtered_results['confidence'] < 50)
                ]
            
            # Display relevant columns
            display_columns = ['name', 'original_address', 'formatted_address', 'is_valid', 'confidence', 'error']
            available_columns = [col for col in display_columns if col in filtered_results.columns]
            
            # Use safe display method
            self.safe_display_dataframe(filtered_results[available_columns], max_rows=50)
    
    def show_duplicate_results(self, duplicates_df):
        """Display duplicate detection results"""
        st.markdown("### 🔄 Duplicate Detection Results")
        
        if duplicates_df.empty:
            st.success("✅ No duplicates found! All customers are new.")
            return
        
        # Summary statistics
        summary = {
            'total_duplicates': len(duplicates_df),
            'phone_duplicates': len(duplicates_df[duplicates_df['phone_matches'].apply(len) > 0]),
            'address_duplicates': len(duplicates_df[duplicates_df['address_matches'].apply(len) > 0]),
            'both_duplicates': len(duplicates_df[
                (duplicates_df['phone_matches'].apply(len) > 0) & 
                (duplicates_df['address_matches'].apply(len) > 0)
            ])
        }
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Duplicates", summary['total_duplicates'])
        
        with col2:
            st.metric("Phone Matches", summary['phone_duplicates'])
        
        with col3:
            st.metric("Address Matches", summary['address_duplicates'])
        
        with col4:
            st.metric("Both Matches", summary['both_duplicates'])
        
        # Show duplicate breakdown
        st.markdown("#### 📊 Duplicate Types")
        duplicate_types = ['Phone Only', 'Address Only', 'Both Phone & Address']
        duplicate_counts = [
            summary['phone_duplicates'] - summary['both_duplicates'],
            summary['address_duplicates'] - summary['both_duplicates'],
            summary['both_duplicates']
        ]
        
        fig = px.bar(
            x=duplicate_types,
            y=duplicate_counts,
            title="Duplicate Detection Breakdown"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show detailed duplicate results
        with st.expander("📋 Detailed Duplicate Results"):
            for idx, row in duplicates_df.iterrows():
                st.markdown(f"**{row['sms_name']}** (Phone: {row['sms_phone']})")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**SMS Request:**")
                    st.write(f"- Book: {row['sms_book']}")
                    st.write(f"- Language: {row['sms_language']}")
                    st.write(f"- Address: {row['sms_address']}")
                
                with col2:
                    st.markdown("**Previous Records:**")
                    
                    # Show phone matches
                    if row['phone_matches']:
                        st.write("**Phone Matches:**")
                        for match in row['phone_matches'][:3]:  # Show first 3 matches
                            historical_data = match['historical_data']
                            st.write(f"- {historical_data.get('Name', 'Unknown')} - {historical_data.get('Book', '')} ({historical_data.get('Language', '')}) - {historical_data.get('Sent_Date', '')}")
                    
                    # Show address matches
                    if row['address_matches']:
                        st.write("**Address Matches:**")
                        for match in row['address_matches'][:3]:  # Show first 3 matches
                            historical_data = match['historical_data']
                            st.write(f"- {historical_data.get('Name', 'Unknown')} - {historical_data.get('Book', '')} ({historical_data.get('Language', '')}) - {historical_data.get('Sent_Date', '')}")
                
                st.markdown("---")
    
    def show_validation_summary(self, validation_results):
        """Show overall validation summary"""
        st.markdown("### 📊 Validation Summary")
        
        if not validation_results or len(validation_results) == 0:
            st.warning("No validation results available")
            return
        
        # Create summary metrics
        total_records = 0
        valid_phones = 0
        valid_addresses = 0
        
        if 'phones' in validation_results and validation_results['phones'] is not None:
            phone_df = validation_results['phones']
            if hasattr(phone_df, '__len__'):
                total_records = len(phone_df)
                if 'is_valid' in phone_df.columns:
                    valid_phones = len(phone_df[phone_df['is_valid'] == True])
        
        if 'addresses' in validation_results and validation_results['addresses'] is not None:
            address_df = validation_results['addresses']
            if hasattr(address_df, '__len__'):
                if 'is_valid' in address_df.columns:
                    valid_addresses = len(address_df[address_df['is_valid'] == True])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", total_records)
        
        with col2:
            phone_success_rate = (valid_phones / total_records * 100) if total_records > 0 else 0
            st.metric("Valid Phones", valid_phones, delta=f"{phone_success_rate:.1f}%")
        
        with col3:
            address_success_rate = (valid_addresses / total_records * 100) if total_records > 0 else 0
            st.metric("Valid Addresses", valid_addresses, delta=f"{address_success_rate:.1f}%")
    
    def show_performance_stats(self, parallel_processor):
        """Show performance statistics"""
        st.markdown("### ⚡ Performance Statistics")
        
        stats = parallel_processor.get_performance_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Max Workers", stats['max_workers'])
        
        with col2:
            st.metric("CPU Cores", stats['cpu_count'])
        
        with col3:
            st.metric("Errors", stats['errors'])
        
        with col4:
            efficiency = (stats['max_workers'] / stats['cpu_count']) * 100
            st.metric("Efficiency", f"{efficiency:.1f}%")
        
        if stats['errors'] > 0:
            st.warning(f"⚠️ {stats['errors']} errors occurred during processing")
            with st.expander("Error Details"):
                for error in stats['error_details']:
                    st.error(error)
        
        # Performance tips
        st.markdown("#### 💡 Performance Tips")
        tips = [
            "🚀 **Parallel Processing**: Enable for faster execution on large datasets",
            "👥 **Workers**: More workers = faster processing, but uses more resources",
            "📦 **Chunk Size**: Larger chunks = less overhead, smaller chunks = better progress tracking",
            "🌐 **API Limits**: Address validation is limited by Google API rate limits",
            "💾 **Memory**: Large datasets may require more memory with parallel processing"
        ]
        
        for tip in tips:
            st.markdown(tip)
    
    def show_pending_messages(self, processed_data):
        """Show messages that are ready to be sent"""
        st.markdown("### 📱 Messages Ready to Send")
        
        if processed_data is None or processed_data.empty:
            st.warning("No processed data available")
            return
        
        # Group by message type
        message_types = processed_data['message_type'].value_counts()
        
        st.markdown("#### 📊 Message Types")
        fig = px.pie(
            values=message_types.values,
            names=message_types.index,
            title="Distribution of Message Types"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show pending messages
        with st.expander("📋 Pending Messages"):
            for message_type in message_types.index:
                st.markdown(f"**{message_type} Messages:**")
                type_data = processed_data[processed_data['message_type'] == message_type]
                
                for idx, row in type_data.head(5).iterrows():  # Show first 5
                    st.markdown(f"**{row['name']}** ({row['phone']})")
                    st.text_area(
                        f"Message for {row['name']}",
                        value=row['message'],
                        height=100,
                        key=f"message_{idx}"
                    )
                    st.markdown("---")
    
    def show_message_confirmation(self, sms_data, duplicates, message_sender):
        """Show confirmation UI before sending messages"""
        logger.info(f"🔍 show_message_confirmation called with {len(sms_data)} SMS records")
        logger.info(f"🔍 Duplicates: {duplicates is not None and not duplicates.empty if duplicates is not None else 'None'}")
        
        st.markdown("### ✅ Confirm Message Sending")
        
        if duplicates is not None and not duplicates.empty:
            st.warning(f"⚠️ {len(duplicates)} duplicate customers found. They will receive repeat customer messages.")
        
        # Show message preview
        st.markdown("#### 📋 Message Preview")
        
        # Sample a few messages to show
        sample_size = min(3, len(sms_data))
        sample_data = sms_data.head(sample_size)
        logger.info(f"🔍 Showing preview for {sample_size} messages")
        
        for idx, row in sample_data.iterrows():
            st.markdown(f"**{row['Name']}** ({row['Phone']})")
            
            # Generate appropriate message
            if duplicates is not None and not duplicates.empty:
                duplicate_record = duplicates[duplicates['sms_index'] == idx]
                if not duplicate_record.empty:
                    message = message_sender.get_duplicate_message_template(duplicate_record.iloc[0])
                else:
                    has_book_language = bool(row.get('Book') and row.get('Language'))
                    message = message_sender.get_new_customer_message_template(row, has_book_language)
            else:
                has_book_language = bool(row.get('Book') and row.get('Language'))
                message = message_sender.get_new_customer_message_template(row, has_book_language)
            
            st.text_area(
                f"Message for {row['Name']}",
                value=message,
                height=150,
                key=f"preview_{idx}"
            )
            st.markdown("---")
        
        # Confirmation buttons
        logger.info("🔍 Rendering confirmation buttons...")
        
        st.info("💡 Click 'Send SMS' button above to send messages directly")
        
        logger.info("🔍 All confirmation buttons rendered successfully!")
    
    def show_analytics(self, sms_data):
        """Show comprehensive analytics and reports from All_Sent_Records.xlsx"""
        st.markdown("### 📊 Analytics Dashboard - All Sent Records")
        
        # Load all historical data from All_Sent_Records.xlsx
        historical_data = self._load_historical_data()
        
        if historical_data.empty:
            st.warning("⚠️ No historical data found in All_Sent_Records.xlsx")
            return
        
        st.info(f"📊 Showing analytics for **{len(historical_data)}** records from All_Sent_Records.xlsx")
        
        # Create tabs for different analytics sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📚 Books & Languages", "🗺️ Geographic", "📈 Trends & Time", "📊 Summary Stats", "🔍 Data Quality"])
        
        with tab1:
            self._show_book_language_analytics(historical_data)
        
        with tab2:
            self._show_geographic_analytics(historical_data)
        
        with tab3:
            self._show_trend_analytics(historical_data)
        
        with tab4:
            self._show_summary_statistics(historical_data)
        
        with tab5:
            self._show_data_quality_metrics(historical_data)
    
    def _show_book_language_analytics(self, historical_data):
        """Show book and language distribution analytics from All_Sent_Records.xlsx"""
        st.markdown("#### 📚 Book & Language Analytics - All Sent Records")
        
        col1, col2 = st.columns(2)
        
        with col1:
        # Book distribution
            if 'Book' in historical_data.columns:
                book_counts = historical_data['Book'].value_counts()
                st.markdown("**Book Requests Distribution**")
            fig = px.bar(
                x=book_counts.index,
                y=book_counts.values,
                    title="Book Requests by Type",
                    color=book_counts.values,
                    color_continuous_scale='Blues'
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
        # Language distribution
            if 'Language' in historical_data.columns:
                language_counts = historical_data['Language'].value_counts()
                st.markdown("**Language Distribution**")
            fig = px.pie(
                values=language_counts.values,
                names=language_counts.index,
                title="Requests by Language"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Book-Language combination analysis
        if 'Book' in historical_data.columns and 'Language' in historical_data.columns:
            st.markdown("**Book-Language Combination Analysis**")
            book_lang_combo = historical_data.groupby(['Book', 'Language']).size().reset_index(name='Count')
            book_lang_combo['Combination'] = book_lang_combo['Book'] + ' - ' + book_lang_combo['Language']
            
            fig = px.bar(
                book_lang_combo,
                x='Combination',
                y='Count',
                title="Most Popular Book-Language Combinations",
                color='Count',
                color_continuous_scale='Viridis'
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_geographic_analytics(self, historical_data):
        """Show geographic distribution analytics from All_Sent_Records.xlsx"""
        st.markdown("#### 🗺️ Geographic Analytics - All Sent Records")
        
        # Extract geographic information from historical addresses
        geographic_data = self._extract_geographic_data(historical_data)
        
        if not geographic_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # State distribution
                state_counts = geographic_data['State'].value_counts()
                st.markdown("**Requests by State**")
                fig = px.bar(
                    x=state_counts.index,
                    y=state_counts.values,
                    title="Book Requests by State",
                    color=state_counts.values,
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig, use_container_width=True)
        
                # Show state statistics
                st.markdown("**State Statistics**")
                for state, count in state_counts.head(10).items():
                    percentage = (count / len(geographic_data)) * 100
                    st.metric(f"{state}", f"{count} requests", f"{percentage:.1f}%")
            
            with col2:
                # City distribution (top 15)
                city_counts = geographic_data['City'].value_counts().head(15)
                st.markdown("**Top 15 Cities by Requests**")
                fig = px.bar(
                    x=city_counts.values,
                    y=city_counts.index,
                    orientation='h',
                    title="Top Cities by Book Requests",
                    color=city_counts.values,
                    color_continuous_scale='Greens'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Data source breakdown (all historical data)
            st.markdown("**Data Source: All Historical Records**")
            st.info("📊 All data comes from All_Sent_Records.xlsx historical records")
            
            # State-Book analysis
            if 'Book' in historical_data.columns:
                st.markdown("**Book Distribution by State**")
                state_book_data = geographic_data.merge(historical_data[['Book']], left_index=True, right_index=True)
                state_book_counts = state_book_data.groupby(['State', 'Book']).size().reset_index(name='Count')
                
                # Create a pivot table for better visualization
                pivot_data = state_book_counts.pivot(index='State', columns='Book', values='Count').fillna(0)
                
                fig = px.imshow(
                    pivot_data.values,
                    x=pivot_data.columns,
                    y=pivot_data.index,
                    title="Book Requests Heatmap by State (All Data)",
                    color_continuous_scale='Blues',
                    aspect='auto'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # City-Book analysis for top cities
            if 'Book' in historical_data.columns:
                st.markdown("**Book Distribution by Top Cities**")
                top_cities = geographic_data['City'].value_counts().head(10).index
                city_book_data = geographic_data[geographic_data['City'].isin(top_cities)].merge(
                    historical_data[['Book']], left_index=True, right_index=True
                )
                city_book_counts = city_book_data.groupby(['City', 'Book']).size().reset_index(name='Count')
                
                fig = px.bar(
                    city_book_counts,
                    x='City',
                    y='Count',
                    color='Book',
                    title="Book Distribution in Top Cities (All Data)",
                    barmode='stack'
                )
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
            
            # Historical data by state (all data is historical)
            if 'Book' in historical_data.columns:
                st.markdown("**Historical Requests by State**")
                state_book_data = geographic_data.merge(historical_data[['Book']], left_index=True, right_index=True)
                state_counts = state_book_data.groupby('State').size().reset_index(name='Count')
                
                # Get top 10 states for comparison
                top_states = geographic_data['State'].value_counts().head(10).index
                state_filtered = state_counts[state_counts['State'].isin(top_states)]
                
                fig = px.bar(
                    state_filtered,
                    x='State',
                    y='Count',
                    title="Historical Requests by Top States",
                    color='Count',
                    color_continuous_scale='Blues'
                )
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
    
    def _extract_geographic_data(self, sms_data):
        """Extract state and city information from addresses"""
        geographic_info = []
        
        for idx, address in sms_data['Address'].dropna().items():
            address_str = str(address).upper()
            state = 'Unknown'
            city = 'Unknown'
            
            # Extract state
            if 'CA' in address_str or 'CALIFORNIA' in address_str:
                state = 'CA'
            elif 'TX' in address_str or 'TEXAS' in address_str:
                state = 'TX'
            elif 'NY' in address_str or 'NEW YORK' in address_str:
                state = 'NY'
            elif 'FL' in address_str or 'FLORIDA' in address_str:
                state = 'FL'
            elif 'WA' in address_str or 'WASHINGTON' in address_str:
                state = 'WA'
            elif 'IL' in address_str or 'ILLINOIS' in address_str:
                state = 'IL'
            elif 'NJ' in address_str or 'NEW JERSEY' in address_str:
                state = 'NJ'
            elif 'PA' in address_str or 'PENNSYLVANIA' in address_str:
                state = 'PA'
            elif 'GA' in address_str or 'GEORGIA' in address_str:
                state = 'GA'
            elif 'NC' in address_str or 'NORTH CAROLINA' in address_str:
                state = 'NC'
            elif 'VA' in address_str or 'VIRGINIA' in address_str:
                state = 'VA'
            elif 'OH' in address_str or 'OHIO' in address_str:
                state = 'OH'
            elif 'MI' in address_str or 'MICHIGAN' in address_str:
                state = 'MI'
            elif 'AZ' in address_str or 'ARIZONA' in address_str:
                state = 'AZ'
            elif 'TN' in address_str or 'TENNESSEE' in address_str:
                state = 'TN'
            elif 'IN' in address_str or 'INDIANA' in address_str:
                state = 'IN'
            elif 'MA' in address_str or 'MASSACHUSETTS' in address_str:
                state = 'MA'
            elif 'MD' in address_str or 'MARYLAND' in address_str:
                state = 'MD'
            elif 'CO' in address_str or 'COLORADO' in address_str:
                state = 'CO'
            elif 'OR' in address_str or 'OREGON' in address_str:
                state = 'OR'
            elif 'UT' in address_str or 'UTAH' in address_str:
                state = 'UT'
            elif 'NV' in address_str or 'NEVADA' in address_str:
                state = 'NV'
            elif 'CT' in address_str or 'CONNECTICUT' in address_str:
                state = 'CT'
            elif 'WI' in address_str or 'WISCONSIN' in address_str:
                state = 'WI'
            elif 'MN' in address_str or 'MINNESOTA' in address_str:
                state = 'MN'
            elif 'MO' in address_str or 'MISSOURI' in address_str:
                state = 'MO'
            elif 'LA' in address_str or 'LOUISIANA' in address_str:
                state = 'LA'
            elif 'AL' in address_str or 'ALABAMA' in address_str:
                state = 'AL'
            elif 'SC' in address_str or 'SOUTH CAROLINA' in address_str:
                state = 'SC'
            elif 'KY' in address_str or 'KENTUCKY' in address_str:
                state = 'KY'
            elif 'OK' in address_str or 'OKLAHOMA' in address_str:
                state = 'OK'
            elif 'IA' in address_str or 'IOWA' in address_str:
                state = 'IA'
            elif 'AR' in address_str or 'ARKANSAS' in address_str:
                state = 'AR'
            elif 'KS' in address_str or 'KANSAS' in address_str:
                state = 'KS'
            elif 'NM' in address_str or 'NEW MEXICO' in address_str:
                state = 'NM'
            elif 'NE' in address_str or 'NEBRASKA' in address_str:
                state = 'NE'
            elif 'WV' in address_str or 'WEST VIRGINIA' in address_str:
                state = 'WV'
            elif 'ID' in address_str or 'IDAHO' in address_str:
                state = 'ID'
            elif 'HI' in address_str or 'HAWAII' in address_str:
                state = 'HI'
            elif 'NH' in address_str or 'NEW HAMPSHIRE' in address_str:
                state = 'NH'
            elif 'ME' in address_str or 'MAINE' in address_str:
                state = 'ME'
            elif 'RI' in address_str or 'RHODE ISLAND' in address_str:
                state = 'RI'
            elif 'MT' in address_str or 'MONTANA' in address_str:
                state = 'MT'
            elif 'DE' in address_str or 'DELAWARE' in address_str:
                state = 'DE'
            elif 'SD' in address_str or 'SOUTH DAKOTA' in address_str:
                state = 'SD'
            elif 'ND' in address_str or 'NORTH DAKOTA' in address_str:
                state = 'ND'
            elif 'AK' in address_str or 'ALASKA' in address_str:
                state = 'AK'
            elif 'VT' in address_str or 'VERMONT' in address_str:
                state = 'VT'
            elif 'WY' in address_str or 'WYOMING' in address_str:
                state = 'WY'
            else:
                state = 'Other'
            
            # Extract city (simplified - look for common city patterns)
            address_parts = address_str.split()
            for i, part in enumerate(address_parts):
                # Look for city names (usually before state)
                if part in ['ST', 'STREET', 'AVE', 'AVENUE', 'RD', 'ROAD', 'BLVD', 'BOULEVARD', 'DR', 'DRIVE', 'CT', 'COURT', 'LN', 'LANE', 'PL', 'PLACE', 'WAY', 'CIR', 'CIRCLE']:
                    if i > 0:
                        city = address_parts[i-1].title()
                        break
                # Look for common city indicators
                elif part in ['CITY', 'TOWN', 'VILLAGE']:
                    if i > 0:
                        city = address_parts[i-1].title()
                        break
            
            # If no city found, try to extract from common patterns
            if city == 'Unknown':
                # Look for patterns like "City, State" or "City State"
                for i, part in enumerate(address_parts):
                    if part == state or part in ['CA', 'TX', 'NY', 'FL', 'WA', 'IL', 'NJ', 'PA', 'GA', 'NC', 'VA', 'OH', 'MI', 'AZ', 'TN', 'IN', 'MA', 'MD', 'CO', 'OR', 'UT', 'NV', 'CT', 'WI', 'MN', 'MO', 'LA', 'AL', 'SC', 'KY', 'OK', 'IA', 'AR', 'KS', 'NM', 'NE', 'WV', 'ID', 'HI', 'NH', 'ME', 'RI', 'MT', 'DE', 'SD', 'ND', 'AK', 'VT', 'WY']:
                        if i > 0:
                            city = address_parts[i-1].title()
                            break
            
            geographic_info.append({
                'State': state,
                'City': city
            })
        
        return pd.DataFrame(geographic_info, index=sms_data['Address'].dropna().index)
    
    def _load_historical_data(self):
        """Load historical data from All_Sent_Records.xlsx"""
        try:
            import os
            historical_file = "All_Sent_Records.xlsx"
            if os.path.exists(historical_file):
                df = pd.read_excel(historical_file)
                logger.info(f"📊 Loaded {len(df)} historical records from {historical_file}")
                return df
            else:
                logger.info("📊 No historical records file found")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"❌ Error loading historical data: {e}")
            return pd.DataFrame()
    
    def _combine_current_and_historical_data(self, sms_data, historical_data):
        """Combine current SMS data with historical data for comprehensive analytics"""
        try:
            # Prepare current SMS data
            current_data = sms_data.copy()
            current_data['Data_Source'] = 'Current'
            
            # Prepare historical data
            if not historical_data.empty:
                # Select relevant columns from historical data
                historical_columns = ['Name', 'Phone', 'Address', 'Book', 'Language', 'Email', 'City', 'State', 'Zip_Code', 'Country']
                available_columns = [col for col in historical_columns if col in historical_data.columns]
                historical_subset = historical_data[available_columns].copy()
                historical_subset['Data_Source'] = 'Historical'
                
                # Combine the datasets
                combined_data = pd.concat([current_data, historical_subset], ignore_index=True)
                logger.info(f"📊 Combined data: {len(current_data)} current + {len(historical_subset)} historical = {len(combined_data)} total records")
            else:
                combined_data = current_data
                logger.info(f"📊 Using only current data: {len(combined_data)} records")
            
            return combined_data
            
        except Exception as e:
            logger.error(f"❌ Error combining data: {e}")
            return sms_data
    
    def _show_trend_analytics(self, historical_data):
        """Show time-based trend analytics from All_Sent_Records.xlsx"""
        st.markdown("#### 📈 Trend Analytics - All Sent Records")
        
        # Date-based analysis
        if 'Sent_Date' in historical_data.columns:
            # Convert date column to datetime, handling mixed types
            historical_data_copy = historical_data.copy()
            historical_data_copy['Sent_Date'] = pd.to_datetime(historical_data_copy['Sent_Date'], errors='coerce')
            
            # Filter out invalid dates (NaT values)
            valid_dates = historical_data_copy.dropna(subset=['Sent_Date'])
            
            if valid_dates.empty:
                st.warning("⚠️ No valid dates found in Sent_Date column")
                return
            
            if not valid_dates.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Daily trend
                    daily_counts = valid_dates.groupby(valid_dates['Sent_Date'].dt.date).size()
                    st.markdown("**Daily Request Trends**")
                    fig = px.line(
                        x=daily_counts.index,
                        y=daily_counts.values,
                        title="Book Requests Over Time (Daily)"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Monthly trend
                    monthly_counts = valid_dates.groupby(valid_dates['Sent_Date'].dt.to_period('M')).size()
                    st.markdown("**Monthly Request Trends**")
                    fig = px.bar(
                        x=[str(period) for period in monthly_counts.index],
                        y=monthly_counts.values,
                        title="Book Requests by Month"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Book trends over time
                if 'Book' in historical_data.columns:
                    st.markdown("**Book Request Trends Over Time**")
                    book_trends = valid_dates.groupby([valid_dates['Sent_Date'].dt.to_period('M'), 'Book']).size().reset_index(name='Count')
                    book_trends['Period'] = book_trends['Sent_Date'].astype(str)
                    
                    fig = px.line(
                        book_trends,
                        x='Period',
                        y='Count',
                        color='Book',
                        title="Book Request Trends by Month"
                    )
                    fig.update_xaxes(tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
        
        # Year-over-year comparison
        if not valid_dates.empty:
            st.markdown("**Year-over-Year Comparison**")
            
            # Get data by year
            yearly_counts = valid_dates.groupby(valid_dates['Sent_Date'].dt.year).size()
            
            if len(yearly_counts) > 1:
                fig = px.bar(
                    x=yearly_counts.index,
                    y=yearly_counts.values,
                    title="Book Requests by Year",
                    labels={'x': 'Year', 'y': 'Number of Requests'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"Data available for {len(yearly_counts)} year(s): {list(yearly_counts.index)}")
    
    def _show_summary_statistics(self, historical_data):
        """Show comprehensive summary statistics from All_Sent_Records.xlsx"""
        st.markdown("#### 📊 Summary Statistics - All Sent Records")
        
        # Key Performance Indicators
        st.markdown("**Key Performance Indicators (All Sent Records)**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_requests = len(historical_data)
            st.metric("Total Requests", total_requests)
        
        with col2:
            unique_books = historical_data['Book'].nunique() if 'Book' in historical_data.columns else 0
            st.metric("Unique Books", unique_books)
        
        with col3:
            unique_languages = historical_data['Language'].nunique() if 'Language' in historical_data.columns else 0
            st.metric("Languages", unique_languages)
        
        with col4:
            # Calculate geographic diversity from historical data
            geographic_data = self._extract_geographic_data(historical_data)
            unique_states = geographic_data['State'].nunique() if not geographic_data.empty else 0
            st.metric("States Covered", unique_states)
        
        # Top performers
        st.markdown("**Top Performers (All Data)**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Book' in historical_data.columns:
                top_book = historical_data['Book'].value_counts().index[0]
                top_book_count = historical_data['Book'].value_counts().iloc[0]
                st.metric("Most Requested Book", f"{top_book}", f"{top_book_count} requests")
            
            if 'Language' in historical_data.columns:
                top_language = historical_data['Language'].value_counts().index[0]
                top_language_count = historical_data['Language'].value_counts().iloc[0]
                st.metric("Most Requested Language", f"{top_language}", f"{top_language_count} requests")
        
        with col2:
            if not geographic_data.empty:
                top_state = geographic_data['State'].value_counts().index[0]
                top_state_count = geographic_data['State'].value_counts().iloc[0]
                st.metric("Top State", f"{top_state}", f"{top_state_count} requests")
                
                top_city = geographic_data['City'].value_counts().index[0]
                top_city_count = geographic_data['City'].value_counts().iloc[0]
                st.metric("Top City", f"{top_city}", f"{top_city_count} requests")
        
        # Distribution insights
        st.markdown("**Distribution Insights (All Data)**")
        
        if 'Book' in historical_data.columns:
            book_distribution = historical_data['Book'].value_counts()
            most_popular_share = (book_distribution.iloc[0] / len(historical_data)) * 100
            st.info(f"📚 The most popular book ({book_distribution.index[0]}) represents {most_popular_share:.1f}% of all requests")
        
        if 'Language' in historical_data.columns:
            language_distribution = historical_data['Language'].value_counts()
            english_share = (language_distribution.get('English', 0) / len(historical_data)) * 100
            st.info(f"🌍 English requests represent {english_share:.1f}% of all requests")
        
        if not geographic_data.empty:
            state_distribution = geographic_data['State'].value_counts()
            top_state_share = (state_distribution.iloc[0] / len(geographic_data)) * 100
            st.info(f"🗺️ The top state ({state_distribution.index[0]}) represents {top_state_share:.1f}% of all requests")
        
        # All data is historical from All_Sent_Records.xlsx
        st.markdown("**Data Source: All Historical Records**")
        st.info("📊 All data comes from All_Sent_Records.xlsx historical records")
    
    def _show_data_quality_metrics(self, historical_data):
        """Show data quality metrics from All_Sent_Records.xlsx"""
        st.markdown("#### 📈 Data Quality Metrics - All Sent Records")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            completeness = (1 - historical_data.isnull().sum().sum() / (len(historical_data) * len(historical_data.columns))) * 100
            st.metric("Overall Completeness", f"{completeness:.1f}%")
        
        with col2:
            if 'Book' in historical_data.columns:
                book_completeness = (1 - historical_data['Book'].isnull().sum() / len(historical_data)) * 100
                st.metric("Book Completeness", f"{book_completeness:.1f}%")
        
        with col3:
            if 'Language' in historical_data.columns:
                language_completeness = (1 - historical_data['Language'].isnull().sum() / len(historical_data)) * 100
                st.metric("Language Completeness", f"{language_completeness:.1f}%")
        
        with col4:
            if 'Phone' in historical_data.columns:
                phone_completeness = (1 - historical_data['Phone'].isnull().sum() / len(historical_data)) * 100
                st.metric("Phone Completeness", f"{phone_completeness:.1f}%")
        
        # Detailed quality analysis
        st.markdown("**Detailed Quality Analysis**")
        
        quality_metrics = []
        for column in historical_data.columns:
            if column in ['Name', 'Phone', 'Address', 'Book', 'Language', 'Email']:
                null_count = historical_data[column].isnull().sum()
                null_percentage = (null_count / len(historical_data)) * 100
                quality_metrics.append({
                    'Field': column,
                    'Missing Count': null_count,
                    'Missing %': f"{null_percentage:.1f}%",
                    'Quality Score': f"{100 - null_percentage:.1f}%"
                })
        
        if quality_metrics:
            quality_df = pd.DataFrame(quality_metrics)
            st.dataframe(quality_df, use_container_width=True)
        
        # Data validation insights
        st.markdown("**Data Validation Insights**")
        
        if 'Phone' in historical_data.columns:
            # Check for valid phone number patterns
            phone_pattern = r'^\d{10}$'
            valid_phones = historical_data['Phone'].astype(str).str.match(phone_pattern).sum()
            phone_validity = (valid_phones / len(historical_data)) * 100
            st.info(f"📱 {phone_validity:.1f}% of phone numbers follow the 10-digit format")
        
        if 'Address' in historical_data.columns:
            # Check for complete addresses
            complete_addresses = historical_data['Address'].dropna().apply(
                lambda x: len(str(x).split()) >= 3
            ).sum()
            address_completeness = (complete_addresses / len(historical_data)) * 100
            st.info(f"🏠 {address_completeness:.1f}% of addresses appear to be complete (3+ words)")
    
    def _send_whatsapp_messages(self, sms_data, duplicates, message_sender):
        """Send WhatsApp messages to all recipients"""
        import pandas as pd
        from datetime import datetime
        import logging
        
        logger = logging.getLogger(__name__)
        
        st.markdown("### 💬 Sending WhatsApp Messages...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = []
        for i, (idx, row) in enumerate(sms_data.iterrows()):
            progress = (i + 1) / len(sms_data)
            progress_bar.progress(min(progress, 1.0))  # Ensure progress never exceeds 1.0
            status_text.text(f"Sending WhatsApp to {row['Name']} ({i + 1}/{len(sms_data)})")
            
            logger.info(f"📱 Processing WhatsApp for {row['Name']} - Phone: {row['Phone']}")
            
            # Skip if name or phone is empty
            if not row.get('Name') or not row.get('Phone'):
                logger.info(f"⏭️ Skipping {row.get('Name', 'Unknown')} - empty name or phone")
                self._record_duplicate_transaction(row, "Empty name or phone number")
                
                result = {
                    'success': False,
                    'error': 'Empty name or phone number',
                    'name': row.get('Name', ''),
                    'phone': row.get('Phone', ''),
                    'skipped': True,
                    'record_index': idx
                }
                results.append(result)
                continue
            
            # Check if this person has already been sent a WhatsApp message for the same book
            # Use the same book defaulting logic as in message generation
            book = row.get('Book', '')
            if pd.isna(book) or book == '' or str(book).lower() == 'nan':
                book = 'GG'
            
            if self._was_message_already_sent(row['Name'], row['Phone'], book, 'WhatsApp'):
                logger.info(f"⏭️ Skipping {row['Name']} - WhatsApp message already sent for this book previously")
                self._record_duplicate_transaction(row, "WhatsApp message already sent for this book previously")
                
                # Add a skipped result
                result = {
                    'success': False,
                    'error': 'WhatsApp message already sent for this book previously',
                    'name': row['Name'],
                    'phone': row['Phone'],
                    'skipped': True,
                    'record_index': idx
                }
                results.append(result)
                continue
            
            # Generate message based on duplicate status
            # Check if person is a historical customer
            is_historical_customer = self._is_historical_customer(row['Name'], row['Phone'])
            
            if is_historical_customer:
                logger.info(f"🔍 Historical customer detected for WhatsApp: {row['Name']} - duplicates available: {duplicates is not None}")
                
                # Use duplicate message template for historical customers
                if duplicates is not None and not duplicates.empty:
                    duplicate_record = duplicates[duplicates['sms_index'] == idx]
                    logger.info(f"🔍 Looking for duplicate record with sms_index {idx}, found: {len(duplicate_record)} records")
                    if not duplicate_record.empty:
                        logger.info(f"🔍 DEBUG: Calling get_duplicate_message_template with duplicate record: {duplicate_record.iloc[0].to_dict()}")
                        logger.info(f"🔍 DEBUG: About to call get_duplicate_message_template function")
                        message = message_sender.get_duplicate_message_template(duplicate_record.iloc[0])
                        logger.info(f"🔍 DEBUG: get_duplicate_message_template function returned: {message[:100] if message else 'None'}...")
                        logger.info(f"📝 Using duplicate message template for historical customer: {row['Name']}")
                    else:
                        # Fallback to new customer template if no duplicate record found
                        book = row.get('Book', '')
                        language = row.get('Language', '')
                        if pd.isna(book) or book == '' or str(book).lower() == 'nan':
                            book = 'GG'
                        if pd.isna(language) or language == '' or str(language).lower() == 'nan':
                            language = 'English'
                        
                        corrected_row = row.copy()
                        corrected_row['Book'] = book
                        corrected_row['Language'] = language
                        
                        has_book_language = bool(book and language)
                        message = message_sender.get_new_customer_message_template(corrected_row, has_book_language)
                        logger.info(f"📝 Using new customer template for historical customer (no duplicate record): {row['Name']} - Book: {book}, Language: {language}")
                else:
                    # No duplicates data, use new customer template
                    logger.info(f"❌ PROBLEM: No duplicates data available for historical customer: {row['Name']}")
                    book = row.get('Book', '')
                    language = row.get('Language', '')
                    if pd.isna(book) or book == '' or str(book).lower() == 'nan':
                        book = 'GG'
                    if pd.isna(language) or language == '' or str(language).lower() == 'nan':
                        language = 'English'
                    
                    corrected_row = row.copy()
                    corrected_row['Book'] = book
                    corrected_row['Language'] = language
                    
                    has_book_language = bool(book and language)
                    message = message_sender.get_new_customer_message_template(corrected_row, has_book_language)
                    logger.info(f"📝 Using new customer template for historical customer (no duplicates data): {row['Name']} - Book: {book}, Language: {language}")
            else:
                # New customer, use new customer template
                has_book_language = bool(row.get('Book') and row.get('Language'))
                message = message_sender.get_new_customer_message_template(row, has_book_language)
                logger.info(f"📝 Using new customer template for new customer: {row['Name']}")
            
            logger.info(f"📝 Generated WhatsApp message for {row['Name']}: {message[:100]}...")
            
            # Send WhatsApp message
            logger.info(f"🚀 About to call message_sender.send_whatsapp_message for {row['Name']}")
            result = message_sender.send_whatsapp_message(row['Phone'], message)
            logger.info(f"🚀 WhatsApp send result received: {result}")
            result.update({'name': row['Name'], 'phone': row['Phone'], 'record_index': idx})
            
            # Record failed transactions (invalid phone numbers)
            if not result.get('success') and 'phone' in result.get('error', '').lower():
                self._record_failed_transaction(row, result.get('error', 'Unknown error'))
            
            results.append(result)
            
            # Note: Not adding to memory - only file-based duplicate prevention
            
            logger.info(f"📊 WhatsApp result for {row['Name']}: {result}")
        
        progress_bar.progress(1.0)
        status_text.text("WhatsApp sending complete!")
        
        # Count results
        successful = [r for r in results if r.get('success')]
        skipped = [r for r in results if r.get('skipped')]
        failed = [r for r in results if not r.get('success') and not r.get('skipped')]
        
        successful_count = len(successful)
        skipped_count = len(skipped)
        failed_count = len(failed)
        
        logger.info(f"✅ Batch WhatsApp sending completed. Results: {len(results)} total, {successful_count} successful, {skipped_count} skipped, {failed_count} failed")
        
        # Create new records file with sending results
        self._create_new_records_file(results, "WhatsApp")
        
        # Show results
        self._show_sending_results(results, "WhatsApp")
    
    def _send_sms_messages(self, sms_data, duplicates, message_sender):
        """Send SMS messages to all recipients"""
        import pandas as pd
        from datetime import datetime
        
        logger.info(f"🚀 _send_sms_messages function called!")
        logger.info(f"🚀 Starting batch SMS sending for {len(sms_data)} recipients")
        logger.info(f"🚀 SMS data type: {type(sms_data)}")
        logger.info(f"🚀 Message sender type: {type(message_sender)}")
        st.markdown("### 📱 Sending SMS Messages...")
        
        # Note: Using file-based duplicate prevention (no memory storage)
        logger.info("🔍 Using file-based duplicate prevention")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = []
        skipped_count = 0
        logger.info(f"🚀 About to start loop for {len(sms_data)} records")
        for i, (idx, row) in enumerate(sms_data.iterrows()):
            progress = (i + 1) / len(sms_data)
            progress_bar.progress(min(progress, 1.0))  # Ensure progress never exceeds 1.0
            status_text.text(f"Sending SMS to {row['Name']} ({i + 1}/{len(sms_data)})")
            
            logger.info(f"📱 Processing SMS for {row['Name']} - Phone: {row['Phone']}")
            
            # Skip if name or phone is empty
            if not row.get('Name') or not row.get('Phone') or str(row.get('Name')).strip() == '' or str(row.get('Phone')).strip() == '':
                logger.info(f"⏭️ Skipping empty record - Name: '{row.get('Name')}', Phone: '{row.get('Phone')}'")
                skipped_count += 1
                
                # Record duplicate transaction for empty records
                self._record_duplicate_transaction(row, "Empty name or phone number")
                
                result = {
                    'success': False,
                    'error': 'Empty name or phone number',
                    'name': row.get('Name', ''),
                    'phone': row.get('Phone', ''),
                    'skipped': True
                }
                results.append(result)
                continue
            
            # Check if this person has already been sent a message for the same book
            # Use the same book defaulting logic as in message generation
            book = row.get('Book', '')
            if pd.isna(book) or book == '' or str(book).lower() == 'nan':
                book = 'GG'
            
            if self._was_message_already_sent(row['Name'], row['Phone'], book):
                logger.info(f"⏭️ Skipping {row['Name']} - message already sent for this book previously")
                skipped_count += 1
                
                # Record duplicate transaction
                self._record_duplicate_transaction(row, "Same book already sent")
                
                # Add a skipped result
                result = {
                    'success': False,
                    'error': 'Message already sent for this book previously',
                    'name': row['Name'],
                    'phone': row['Phone'],
                    'skipped': True
                }
                results.append(result)
                continue
            
            # Generate message based on duplicate status
            # Check if person is a historical customer
            is_historical_customer = self._is_historical_customer(row['Name'], row['Phone'])
            
            if is_historical_customer:
                logger.info(f"🔍 Historical customer detected: {row['Name']} - duplicates available: {duplicates is not None}")
                if duplicates is not None:
                    logger.info(f"🔍 Duplicates data: {len(duplicates)} records, empty: {duplicates.empty}")
                else:
                    logger.info(f"🔍 Duplicates is None - this is the problem!")
                
                # Use duplicate message template for historical customers
                if duplicates is not None and not duplicates.empty:
                    duplicate_record = duplicates[duplicates['sms_index'] == idx]
                    logger.info(f"🔍 Looking for duplicate record with sms_index {idx}, found: {len(duplicate_record)} records")
                    if not duplicate_record.empty:
                        message = message_sender.get_duplicate_message_template(duplicate_record.iloc[0])
                        logger.info(f"📝 Using duplicate message template for historical customer: {row['Name']}")
                    else:
                        # Fallback to new customer template if no duplicate record found
                        book = row.get('Book', '')
                        language = row.get('Language', '')
                        if pd.isna(book) or book == '' or str(book).lower() == 'nan':
                            book = 'GG'
                        if pd.isna(language) or language == '' or str(language).lower() == 'nan':
                            language = 'English'
                        
                        corrected_row = row.copy()
                        corrected_row['Book'] = book
                        corrected_row['Language'] = language
                        
                        has_book_language = bool(book and language)
                        message = message_sender.get_new_customer_message_template(corrected_row, has_book_language)
                        logger.info(f"📝 Using new customer template for historical customer (no duplicate record): {row['Name']} - Book: {book}, Language: {language}")
                else:
                    # No duplicates data, use new customer template
                    logger.info(f"❌ PROBLEM: No duplicates data available for historical customer: {row['Name']}")
                    book = row.get('Book', '')
                    language = row.get('Language', '')
                    if pd.isna(book) or book == '' or str(book).lower() == 'nan':
                        book = 'GG'
                    if pd.isna(language) or language == '' or str(language).lower() == 'nan':
                        language = 'English'
                    
                    corrected_row = row.copy()
                    corrected_row['Book'] = book
                    corrected_row['Language'] = language
                    
                    has_book_language = bool(book and language)
                    message = message_sender.get_new_customer_message_template(corrected_row, has_book_language)
                    logger.info(f"📝 Using new customer template for historical customer (no duplicates data): {row['Name']} - Book: {book}, Language: {language}")
            else:
                # New customer - use new customer template
                book = row.get('Book', '')
                language = row.get('Language', '')
                if pd.isna(book) or book == '' or str(book).lower() == 'nan':
                    book = 'GG'
                if pd.isna(language) or language == '' or str(language).lower() == 'nan':
                    language = 'English'
                
                corrected_row = row.copy()
                corrected_row['Book'] = book
                corrected_row['Language'] = language
                
                has_book_language = bool(book and language)
                message = message_sender.get_new_customer_message_template(corrected_row, has_book_language)
                logger.info(f"📝 Using new customer template for new customer: {row['Name']} - Book: {book}, Language: {language}")
            
            logger.info(f"📝 Generated message for {row['Name']}: {message[:100]}...")
            
            # Send SMS message
            logger.info(f"🚀 About to call message_sender.send_sms_message for {row['Name']}")
            result = message_sender.send_sms_message(row['Phone'], message)
            logger.info(f"🚀 SMS send result received: {result}")
            result.update({'name': row['Name'], 'phone': row['Phone'], 'record_index': idx})
            
            # Record failed transactions (invalid phone numbers)
            if not result.get('success') and 'phone' in result.get('error', '').lower():
                self._record_failed_transaction(row, result.get('error', 'Unknown error'))
            
            results.append(result)
            
            # Note: Not adding to memory - only file-based duplicate prevention
            
            logger.info(f"📊 SMS result for {row['Name']}: {result}")
        
        progress_bar.progress(1.0)
        status_text.text("SMS sending complete!")
        
        successful_count = sum(1 for r in results if r.get('success'))
        skipped_count = sum(1 for r in results if r.get('skipped'))
        failed_count = len(results) - successful_count - skipped_count
        
        logger.info(f"✅ Batch SMS sending completed. Results: {len(results)} total, {successful_count} successful, {skipped_count} skipped, {failed_count} failed")
        
        # Create new records file with sending results
        self._create_new_records_file(results, "SMS")
        
        # Show results
        self._show_sending_results(results, "SMS")
    
    def _send_both_messages(self, sms_data, duplicates, message_sender):
        """Send both WhatsApp and SMS messages to all recipients"""
        import pandas as pd
        from datetime import datetime
        import logging
        
        logger = logging.getLogger(__name__)
        
        st.markdown("### 🔄 Sending Both WhatsApp and SMS Messages...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = []
        for i, (idx, row) in enumerate(sms_data.iterrows()):
            progress = (i + 1) / len(sms_data)
            progress_bar.progress(min(progress, 1.0))  # Ensure progress never exceeds 1.0
            status_text.text(f"Sending messages to {row['Name']} ({i + 1}/{len(sms_data)})")
            
            logger.info(f"📱 Processing Both for {row['Name']} - Phone: {row['Phone']}")
            
            # Skip if name or phone is empty
            if not row.get('Name') or not row.get('Phone'):
                logger.info(f"⏭️ Skipping {row.get('Name', 'Unknown')} - empty name or phone")
                self._record_duplicate_transaction(row, "Empty name or phone number")
                
                result = {
                    'success': False,
                    'error': 'Empty name or phone number',
                    'name': row.get('Name', ''),
                    'phone': row.get('Phone', ''),
                    'skipped': True,
                    'record_index': idx
                }
                results.append(result)
                continue
            
            # Check if this person has already been sent messages for the same book
            # Use the same book defaulting logic as in message generation
            book = row.get('Book', '')
            if pd.isna(book) or book == '' or str(book).lower() == 'nan':
                book = 'GG'
            
            # Check for both SMS and WhatsApp duplicates
            sms_sent = self._was_message_already_sent(row['Name'], row['Phone'], book, 'SMS')
            whatsapp_sent = self._was_message_already_sent(row['Name'], row['Phone'], book, 'WhatsApp')
            
            if sms_sent and whatsapp_sent:
                logger.info(f"⏭️ Skipping {row['Name']} - Both SMS and WhatsApp messages already sent for this book previously")
                self._record_duplicate_transaction(row, "Both SMS and WhatsApp messages already sent for this book previously")
                
                # Add a skipped result
                result = {
                    'success': False,
                    'error': 'Both SMS and WhatsApp messages already sent for this book previously',
                    'name': row['Name'],
                    'phone': row['Phone'],
                    'skipped': True,
                    'record_index': idx
                }
                results.append(result)
                continue
            
            # Generate message based on duplicate status
            # Check if person is a historical customer
            is_historical_customer = self._is_historical_customer(row['Name'], row['Phone'])
            
            if is_historical_customer:
                logger.info(f"🔍 Historical customer detected for Both: {row['Name']} - duplicates available: {duplicates is not None}")
                
                # Use duplicate message template for historical customers
                if duplicates is not None and not duplicates.empty:
                    duplicate_record = duplicates[duplicates['sms_index'] == idx]
                    logger.info(f"🔍 Looking for duplicate record with sms_index {idx}, found: {len(duplicate_record)} records")
                    if not duplicate_record.empty:
                        logger.info(f"🔍 DEBUG: Calling get_duplicate_message_template with duplicate record: {duplicate_record.iloc[0].to_dict()}")
                        logger.info(f"🔍 DEBUG: About to call get_duplicate_message_template function")
                        message = message_sender.get_duplicate_message_template(duplicate_record.iloc[0])
                        logger.info(f"🔍 DEBUG: get_duplicate_message_template function returned: {message[:100] if message else 'None'}...")
                        logger.info(f"📝 Using duplicate message template for historical customer: {row['Name']}")
                    else:
                        # Fallback to new customer template if no duplicate record found
                        book = row.get('Book', '')
                        language = row.get('Language', '')
                        if pd.isna(book) or book == '' or str(book).lower() == 'nan':
                            book = 'GG'
                        if pd.isna(language) or language == '' or str(language).lower() == 'nan':
                            language = 'English'
                        
                        corrected_row = row.copy()
                        corrected_row['Book'] = book
                        corrected_row['Language'] = language
                        
                        has_book_language = bool(book and language)
                        message = message_sender.get_new_customer_message_template(corrected_row, has_book_language)
                        logger.info(f"📝 Using new customer template for historical customer (no duplicate record): {row['Name']} - Book: {book}, Language: {language}")
                else:
                    # No duplicates data, use new customer template
                    logger.info(f"❌ PROBLEM: No duplicates data available for historical customer: {row['Name']}")
                    book = row.get('Book', '')
                    language = row.get('Language', '')
                    if pd.isna(book) or book == '' or str(book).lower() == 'nan':
                        book = 'GG'
                    if pd.isna(language) or language == '' or str(language).lower() == 'nan':
                        language = 'English'
                    
                    corrected_row = row.copy()
                    corrected_row['Book'] = book
                    corrected_row['Language'] = language
                    
                    has_book_language = bool(book and language)
                    message = message_sender.get_new_customer_message_template(corrected_row, has_book_language)
                    logger.info(f"📝 Using new customer template for historical customer (no duplicates data): {row['Name']} - Book: {book}, Language: {language}")
            else:
                # New customer, use new customer template
                has_book_language = bool(row.get('Book') and row.get('Language'))
                message = message_sender.get_new_customer_message_template(row, has_book_language)
                logger.info(f"📝 Using new customer template for new customer: {row['Name']}")
            
            logger.info(f"📝 Generated message for Both: {row['Name']}: {message[:100]}...")
            
            # Send both messages
            logger.info(f"🚀 About to call message_sender.send_both_messages for {row['Name']}")
            result = message_sender.send_both_messages(row['Phone'], message)
            logger.info(f"🚀 Both send result received: {result}")
            result.update({'name': row['Name'], 'phone': row['Phone'], 'record_index': idx})
            
            # Record failed transactions (invalid phone numbers)
            if not result.get('success') and 'phone' in result.get('error', '').lower():
                self._record_failed_transaction(row, result.get('error', 'Unknown error'))
            
            results.append(result)
            
            # Note: Not adding to memory - only file-based duplicate prevention
            
            logger.info(f"📊 Both result for {row['Name']}: {result}")
        
        progress_bar.progress(1.0)
        status_text.text("Message sending complete!")
        
        # Count results
        successful = [r for r in results if r.get('success')]
        skipped = [r for r in results if r.get('skipped')]
        failed = [r for r in results if not r.get('success') and not r.get('skipped')]
        
        successful_count = len(successful)
        skipped_count = len(skipped)
        failed_count = len(failed)
        
        logger.info(f"✅ Batch Both sending completed. Results: {len(results)} total, {successful_count} successful, {skipped_count} skipped, {failed_count} failed")
        
        # Create new records file with sending results
        self._create_new_records_file(results, "Both")
        
        # Show results
        self._show_sending_results(results, "Both WhatsApp and SMS")
    
    def _show_sending_results(self, results, message_type):
        """Show results of message sending"""
        st.markdown(f"### 📊 {message_type} Sending Results")
        
        successful = [r for r in results if r.get('success')]
        failed = [r for r in results if not r.get('success') and not r.get('skipped')]
        skipped = [r for r in results if r.get('skipped')]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("✅ Successful", len(successful))
        
        with col2:
            st.metric("❌ Failed", len(failed))
        
        with col3:
            st.metric("⏭️ Skipped", len(skipped))
        
        if skipped:
            st.markdown("#### ⏭️ Skipped Messages (Already Sent):")
            for result in skipped:
                st.warning(f"**{result['name']}** ({result['phone']}): {result.get('error', 'Already sent previously')}")
        
        if failed:
            st.markdown("#### ❌ Failed Messages:")
            for result in failed:
                st.error(f"**{result['name']}** ({result['phone']}): {result.get('error', 'Unknown error')}")
        
        if successful:
            st.markdown("#### ✅ Successful Messages:")
            for result in successful[:5]:  # Show first 5 successful
                st.success(f"**{result['name']}** ({result['phone']}) - Message ID: {result.get('message_sid', 'N/A')}")
            
            if len(successful) > 5:
                st.info(f"... and {len(successful) - 5} more successful messages")
        
        st.success(f"🎉 {message_type} sending completed!")
    
    def _create_new_records_file(self, results, message_type):
        """Create a new Excel file with all new records and sending results"""
        try:
            import pandas as pd
            from datetime import datetime
            import os
            
            logger.info(f"📝 Creating new records file with {message_type} sending results...")
            
            # Get SMS data from session state
            if hasattr(st.session_state, 'sms_data') and st.session_state.sms_data is not None:
                sms_df = st.session_state.sms_data.copy()
                logger.info(f"📱 Loaded SMS data with {len(sms_df)} records")
            else:
                logger.warning("⚠️ No SMS data found in session state")
                return
            
            # Create new records DataFrame
            new_records = []
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for result in results:
                # Only record successful messages, skip failed and skipped messages
                if not result.get('success') or result.get('skipped'):
                    logger.info(f"⏭️ Skipping record for {result.get('name', 'Unknown')} - Status: {'Skipped' if result.get('skipped') else 'Failed'}")
                    continue
                    
                name = result.get('name', '')
                phone = result.get('phone', '')
                
                if name and phone:
                    # Find corresponding SMS record using record_index if available, otherwise by name and phone
                    record_index = result.get('record_index')
                    if record_index is not None and record_index in sms_df.index:
                        sms_record = sms_df.loc[record_index]
                    else:
                        # Fallback to name and phone matching
                        sms_mask = (sms_df['Name'] == name) & (sms_df['Phone'] == phone)
                        if sms_mask.any():
                            sms_record = sms_df[sms_mask].iloc[0]
                        else:
                            continue
                    
                    # Create new record with all necessary fields
                    new_record = {
                        # Core identification fields
                        'Name': sms_record.get('Name', ''),
                        'Phone': sms_record.get('Phone', ''),
                        'Address': sms_record.get('Address', ''),
                        
                        # Book and language info with defaults
                        'Book': 'GG' if pd.isna(sms_record.get('Book', '')) or sms_record.get('Book', '') == '' or str(sms_record.get('Book', '')).lower() == 'nan' else sms_record.get('Book', ''),
                        'Language': 'English' if pd.isna(sms_record.get('Language', '')) or sms_record.get('Language', '') == '' or str(sms_record.get('Language', '')).lower() == 'nan' else sms_record.get('Language', ''),
                        
                        # Message sending details
                        'Message_Type': message_type,
                        'Sent_Date': current_time,
                        'Status': "Success",
                        'Message_ID': result.get('message_sid', ''),
                        'Error_Message': '',  # No error message for successful messages
                        
                        # Additional fields from SMS data
                        'Email': sms_record.get('Email', ''),
                        'City': sms_record.get('City', ''),
                        'State': sms_record.get('State', ''),
                        'Zip_Code': sms_record.get('Zip_Code', ''),
                        'Country': sms_record.get('Country', ''),
                        
                        # Validation results (if available)
                        'Phone_Valid': sms_record.get('phone_valid', ''),
                        'Address_Valid': sms_record.get('address_valid', ''),
                        'Carrier_Info': sms_record.get('carrier_info', ''),
                        
                        # Duplicate status (if available)
                        'Is_Duplicate': sms_record.get('is_duplicate', False),
                        'Duplicate_Reason': sms_record.get('duplicate_reason', ''),
                        
                        # Campaign tracking
                        'Campaign_Date': current_time.split(' ')[0],  # Just the date part
                        'Campaign_Type': f"{message_type}_Campaign"
                    }
                    
                    new_records.append(new_record)
                    logger.info(f"📝 Created new record for {name} - Status: Success")
            
            if new_records:
                # Create DataFrame from new records
                new_df = pd.DataFrame(new_records)
                
                # Single file to keep all sent records
                master_file = "All_Sent_Records.xlsx"
                
                if os.path.exists(master_file):
                    # Append to existing file
                    existing_df = pd.read_excel(master_file)
                    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                    combined_df.to_excel(master_file, index=False)
                    logger.info(f"📝 Appended {len(new_records)} successful records to: {master_file}")
                    logger.info(f"📊 Total successful records in file: {len(combined_df)}")
                else:
                    # Create new master file
                    new_df.to_excel(master_file, index=False)
                    logger.info(f"📝 Created new master file: {master_file}")
                    logger.info(f"📊 Saved {len(new_records)} successful records")
            else:
                logger.warning("⚠️ No successful records to save (all messages failed or were skipped)")
            
        except Exception as e:
            logger.error(f"❌ Error creating new records file: {e}")
            # Don't raise the error, just log it so it doesn't break the main flow
    
    def _load_previously_sent_records(self):
        """Load previously sent records from All_Sent_Records.xlsx"""
        try:
            import pandas as pd
            
            sent_records_file = "All_Sent_Records.xlsx"
            if not os.path.exists(sent_records_file):
                logger.info("📝 No previously sent records file found")
                return []
            
            df = pd.read_excel(sent_records_file)
            logger.info(f"📖 Loaded {len(df)} previously sent records")
            return df.to_dict('records')
            
        except Exception as e:
            logger.error(f"❌ Error loading previously sent records: {e}")
            return []
    
    def _was_message_already_sent(self, name, phone, book=None, previously_sent=None):
        """Check if a message was already sent. Only checks All_Sent_Records.xlsx"""
        try:
            import pandas as pd
            
            current_name = str(name).strip().lower()
            current_phone = str(phone).strip()
            current_book = str(book).strip().upper() if book else ''
            
            # Normalize phone number by removing decimal points and converting to integer string
            try:
                # Handle phone numbers like "2065044242.0" -> "2065044242"
                current_phone_normalized = str(int(float(current_phone)))
            except (ValueError, TypeError):
                current_phone_normalized = current_phone
            
            # Check All_Sent_Records.xlsx (contains all historical and recent data)
            sent_records_file = "All_Sent_Records.xlsx"
            if os.path.exists(sent_records_file):
                df = pd.read_excel(sent_records_file)
                if not df.empty:
                    for _, record in df.iterrows():
                        record_name = str(record.get('Name', '')).strip().lower()
                        record_phone = str(record.get('Phone', '')).strip()
                        record_book = str(record.get('Book', '')).strip().upper()
                        
                        # Normalize historical phone number
                        try:
                            record_phone_normalized = str(int(float(record_phone)))
                        except (ValueError, TypeError):
                            record_phone_normalized = record_phone
                        
                        # Check by NAME + normalized phone + book (prevent same person getting same book multiple times)
                        if (record_name == current_name and 
                            record_phone_normalized == current_phone_normalized and 
                            record_phone_normalized != '' and 
                            current_book == record_book and 
                            current_book != ''):
                            logger.info(f"🔍 All_Sent_Records: Found duplicate by name+phone+book: {record.get('Name')} - {record.get('Phone')} - Book: {record_book} - Sent: {record.get('Sent_Date')} - Type: {record.get('Message_Type', 'N/A')}")
                            return True
                        
                        # If same person but different book, allow sending (not a duplicate)
                        if (record_name == current_name and 
                            record_phone_normalized == current_phone_normalized and 
                            current_book != record_book):
                            logger.info(f"🔍 All_Sent_Records: Found previous record with different book: {record.get('Name')} - {record.get('Phone')} - Previous Book: {record_book}, Current Book: {current_book} - ALLOWING")
                            continue
            
            # No duplicates found
            logger.info(f"🔍 No duplicates found for {name} ({phone}) - Book: {current_book}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking if message was already sent: {e}")
            return False
    
    def _is_historical_customer(self, name, phone):
        """Check if person is a historical customer in All_Sent_Records.xlsx"""
        try:
            import pandas as pd
            
            sent_records_file = "All_Sent_Records.xlsx"
            if not os.path.exists(sent_records_file):
                return False
            
            df = pd.read_excel(sent_records_file)
            if df.empty:
                return False
            
            current_name = str(name).strip().lower()
            current_phone = str(phone).strip()
            
            # Check if person exists in All_Sent_Records.xlsx (all records are historical)
            for _, record in df.iterrows():
                record_name = str(record.get('Name', '')).strip().lower()
                record_phone = str(record.get('Phone', '')).strip()
                record_type = str(record.get('Message_Type', '')).strip()
                
                # Match by name or phone (all records in All_Sent_Records.xlsx are historical)
                if ((record_name == current_name and record_name != '') or \
                    (record_phone == current_phone and record_phone != '')):
                    logger.info(f"🔍 Found historical customer in All_Sent_Records: {record.get('Name')} - {record.get('Phone')} - Type: {record_type}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking historical customer: {e}")
            return False
    
    def _record_duplicate_transaction(self, row, reason):
        """Record duplicate transactions in a separate file"""
        try:
            import pandas as pd
            from datetime import datetime
            import os
            
            # Prepare duplicate record
            duplicate_record = {
                'Name': row.get('Name', ''),
                'Phone': row.get('Phone', ''),
                'Address': row.get('Address', ''),
                'Book': row.get('Book', ''),
                'Language': row.get('Language', ''),
                'Email': row.get('Email', ''),
                'City': row.get('City', ''),
                'State': row.get('State', ''),
                'Zip_Code': row.get('Zip_Code', ''),
                'Country': row.get('Country', ''),
                'Duplicate_Reason': reason,
                'Attempt_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Campaign_Date': datetime.now().strftime('%Y-%m-%d'),
                'Status': 'Blocked'
            }
            
            # File to store duplicate transactions
            duplicate_file = "Duplicate_Transactions.xlsx"
            
            # Create DataFrame from duplicate record
            new_df = pd.DataFrame([duplicate_record])
            
            if os.path.exists(duplicate_file):
                # Append to existing file
                existing_df = pd.read_excel(duplicate_file)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                combined_df.to_excel(duplicate_file, index=False)
                logger.info(f"📝 Recorded duplicate transaction in: {duplicate_file}")
            else:
                # Create new duplicate file
                new_df.to_excel(duplicate_file, index=False)
                logger.info(f"📝 Created new duplicate transactions file: {duplicate_file}")
            
        except Exception as e:
            logger.error(f"❌ Error recording duplicate transaction: {e}")
    
    def _record_failed_transaction(self, row, error_message):
        """Record failed transactions (invalid phone numbers) in a separate file"""
        try:
            import pandas as pd
            from datetime import datetime
            import os
            
            # Prepare failed record
            failed_record = {
                'Name': row.get('Name', ''),
                'Phone': row.get('Phone', ''),
                'Address': row.get('Address', ''),
                'Book': row.get('Book', ''),
                'Language': row.get('Language', ''),
                'Email': row.get('Email', ''),
                'City': row.get('City', ''),
                'State': row.get('State', ''),
                'Zip_Code': row.get('Zip_Code', ''),
                'Country': row.get('Country', ''),
                'Error_Message': error_message,
                'Failure_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Campaign_Date': datetime.now().strftime('%Y-%m-%d'),
                'Status': 'Failed',
                'Failure_Type': 'Invalid Phone Number'
            }
            
            # File to store failed transactions
            failed_file = "Failed_Transactions.xlsx"
            
            # Create DataFrame from failed record
            new_df = pd.DataFrame([failed_record])
            
            if os.path.exists(failed_file):
                # Append to existing file
                existing_df = pd.read_excel(failed_file)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                combined_df.to_excel(failed_file, index=False)
                logger.info(f"📝 Recorded failed transaction in: {failed_file}")
            else:
                # Create new failed file
                new_df.to_excel(failed_file, index=False)
                logger.info(f"📝 Created new failed transactions file: {failed_file}")
            
        except Exception as e:
            logger.error(f"❌ Error recording failed transaction: {e}")


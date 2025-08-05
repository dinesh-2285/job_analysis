# src/live_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import json
from datetime import datetime, timedelta
import asyncio
import threading

from src.realtime_processor import RealTimeJobProcessor
from src.job_scraper import JobScrapingEngine

class LiveJobDashboard:
    """
    Live job analytics dashboard with real-time updates
    """
    
    def __init__(self):
        self.processor = RealTimeJobProcessor()
        self.scraper = JobScrapingEngine()
        self.setup_page()
        
        # Initialize session state
        if 'processor_started' not in st.session_state:
            st.session_state.processor_started = False
        
        if 'auto_refresh' not in st.session_state:
            st.session_state.auto_refresh = True
    
    def setup_page(self):
        """Setup Streamlit page"""
        st.set_page_config(
            page_title="Live Job Analytics",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def start_processor(self):
        """Start real-time processor"""
        if not st.session_state.processor_started:
            self.processor.start_real_time_processing()
            st.session_state.processor_started = True
    
    def create_real_time_metrics_display(self):
        """Create real-time metrics display"""
        metrics = self.processor.get_real_time_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Jobs Processed",
                f"{metrics['total_processed']:,}",
                delta=f"+{metrics['processing_rate']:.1f}/s"
            )
        
        with col2:
            st.metric(
                "Queue Size",
                metrics['queue_size'],
                delta=f"Errors: {metrics['errors']}"
            )
        
        with col3:
            st.metric(
                "Cache Size",
                metrics['cache_size'],
                help="Number of analytics cache entries"
            )
        
        with col4:
            st.metric(
                "System Status",
                "🟢 Online" if st.session_state.processor_started else "🔴 Offline",
                help="Real-time processing status"
            )
    
    def create_live_charts(self):
        """Create live updating charts"""
        dashboard_data = self.processor.get_live_dashboard_data()
        
        if not dashboard_data:
            st.warning("No live data available. Please start scraping first.")
            return
        
        # Stream distribution chart
        if dashboard_data.get('stream_distribution'):
            st.subheader("🎯 Live Stream Distribution")
            
            streams = list(dashboard_data['stream_distribution'].keys())
            counts = list(dashboard_data['stream_distribution'].values())
            
            fig_stream = px.bar(
                x=counts[:10],
                y=streams[:10],
                orientation='h',
                title="Top Job Streams (Last 7 Days)",
                labels={'x': 'Number of Jobs', 'y': 'Stream'},
                color=counts[:10],
                color_continuous_scale='viridis'
            )
            fig_stream.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_stream, use_container_width=True)
        
        # Location trends
        if dashboard_data.get('location_trends'):
            st.subheader("🌍 Location Trends")
            
            locations = list(dashboard_data['location_trends'].keys())
            counts = list(dashboard_data['location_trends'].values())
            
            fig_location = px.pie(
                values=counts[:8],
                names=locations[:8],
                title="Job Distribution by Location (Last 7 Days)"
            )
            st.plotly_chart(fig_location, use_container_width=True)
        
        # Top companies
        if dashboard_data.get('top_companies'):
            st.subheader("🏢 Top Hiring Companies")
            
            companies = list(dashboard_data['top_companies'].keys())
            counts = list(dashboard_data['top_companies'].values())
            
            fig_company = px.bar(
                x=companies[:10],
                y=counts[:10],
                title="Most Active Companies (Last 7 Days)",
                labels={'x': 'Company', 'y': 'Job Postings'},
                color=counts[:10],
                color_continuous_scale='blues'
            )
            fig_company.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_company, use_container_width=True)
    
    def create_scraping_controls(self):
        """Create scraping control interface"""
        st.subheader("⚙️ Scraping Controls")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Start Scraping", type="primary"):
                with st.spinner("Starting scraping..."):
                    self.start_processor()
                    total_jobs, saved_jobs = self.processor.force_scrape_and_process()
                    
                st.success(f"✅ Scraped {total_jobs} jobs, saved {saved_jobs} new jobs")
        
        with col2:
            if st.button("🔄 Refresh Data"):
                st.rerun()
        
        with col3:
            auto_refresh = st.checkbox("Auto Refresh", value=st.session_state.auto_refresh)
            st.session_state.auto_refresh = auto_refresh
    
    def create_job_search_interface(self):
        """Create job search interface"""
        st.subheader("🔍 Live Job Search")
        
        # Get recent jobs
        recent_jobs = self.scraper.get_jobs_from_database(limit=1000)
        
        if recent_jobs.empty:
            st.info("No jobs available. Please run scraping first.")
            return
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            streams = ['All'] + list(recent_jobs['stream'].unique())
            selected_stream = st.selectbox("Filter by Stream", streams)
        
        with col2:
            locations = ['All'] + list(recent_jobs['location'].unique())
            selected_location = st.selectbox("Filter by Location", locations)
        
        with col3:
            companies = ['All'] + list(recent_jobs['company'].unique())
            selected_company = st.selectbox("Filter by Company", companies)
        
        # Apply filters
        filtered_jobs = recent_jobs.copy()
        
        if selected_stream != 'All':
            filtered_jobs = filtered_jobs[filtered_jobs['stream'] == selected_stream]
        
        if selected_location != 'All':
            filtered_jobs = filtered_jobs[filtered_jobs['location'] == selected_location]
        
        if selected_company != 'All':
            filtered_jobs = filtered_jobs[filtered_jobs['company'] == selected_company]
        
        # Display results
        st.write(f"Found {len(filtered_jobs)} jobs")
        
        if not filtered_jobs.empty:
            # Display jobs table
            display_columns = ['title', 'company', 'location', 'stream', 'salary', 'date_posted', 'source']
            st.dataframe(
                filtered_jobs[display_columns].head(50),
                use_container_width=True,
                column_config={
                    'title': 'Job Title',
                    'company': 'Company',
                    'location': 'Location',
                    'stream': 'Stream',
                    'salary': 'Salary',
                    'date_posted': 'Date Posted',
                    'source': 'Source'
                }
            )
    
    def create_analytics_insights(self):
        """Create analytics insights section"""
        st.subheader("💡 Live Analytics Insights")
        
        metrics = self.processor.get_real_time_metrics()
        insights = metrics.get('insights', {})
        
        if not insights:
            st.info("No insights available yet. Start scraping to generate insights.")
            return
        
        # Hot streams
        if insights.get('hot_streams'):
            st.write("🔥 **Hot Job Streams:**")
            for stream, count in insights['hot_streams']:
                st.write(f"• {stream}: {count} new jobs")
        
        # Trending locations
        if insights.get('trending_locations'):
            st.write("📈 **Trending Locations:**")
            for location, count in insights['trending_locations']:
                st.write(f"• {location}: {count} new jobs")
        
        # Top companies
        if insights.get('top_companies'):
            st.write("🏢 **Most Active Companies:**")
            for company, count in insights['top_companies']:
                st.write(f"• {company}: {count} new jobs")
        
        # Emerging skills
        if insights.get('emerging_skills'):
            st.write("🛠️ **Emerging Skills:**")
            skills_df = pd.DataFrame(insights['emerging_skills'], columns=['Skill', 'Demand'])
            st.dataframe(skills_df.head(10), use_container_width=True)
    
    def create_export_options(self):
        """Create export options"""
        st.subheader("📥 Export Live Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export Analytics"):
                dashboard_data = self.processor.get_live_dashboard_data()
                
                if dashboard_data:
                    json_data = json.dumps(dashboard_data, indent=2, default=str)
                    st.download_button(
                        label="Download Analytics JSON",
                        data=json_data,
                        file_name=f"live_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        
        with col2:
            if st.button("📋 Export Job Data"):
                recent_jobs = self.scraper.get_jobs_from_database(limit=1000)
                
                if not recent_jobs.empty:
                    csv_data = recent_jobs.to_csv(index=False)
                    st.download_button(
                        label="Download Jobs CSV",
                        data=csv_data,
                        file_name=f"live_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
    
    def run_live_dashboard(self):
        """Run the live dashboard"""
        st.title("📊 Live Job Analytics Dashboard")
        st.markdown("### Real-time job market intelligence")
        
        # Auto-refresh logic
        if st.session_state.auto_refresh:
            # Create a placeholder for auto-refresh
            refresh_placeholder = st.empty()
            with refresh_placeholder.container():
                st.info("🔄 Auto-refresh enabled - Dashboard updates every 30 seconds")
        
        # Real-time metrics
        st.markdown("---")
        self.create_real_time_metrics_display()
        
        # Scraping controls
        st.markdown("---")
        self.create_scraping_controls()
        
        # Main dashboard tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Charts", "🔍 Job Search", "💡 Insights", "📥 Export"])
        
        with tab1:
            self.create_live_charts()
        
        with tab2:
            self.create_job_search_interface()
        
        with tab3:
            self.create_analytics_insights()
        
        with tab4:
            self.create_export_options()
        
        # Auto-refresh mechanism
        if st.session_state.auto_refresh:
            time.sleep(30)
            st.rerun()
        
        # Footer
        st.markdown("---")
        st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown("**Status:** 🟢 Live Data | 🔄 Real-time Processing | 📊 Analytics Active")

# Run the dashboard
if __name__ == "__main__":
    dashboard = LiveJobDashboard()
    dashboard.run_live_dashboard()

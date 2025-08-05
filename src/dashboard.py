# src/dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import json

from src.eda_module import JobAnalyticsEDA
from job_analysis.config import PROCESSED_DATA_PATH

class JobAnalyticsDashboard:
    """
    Interactive Streamlit Dashboard for Job Market Analytics
    """
    
    def __init__(self):
        # --- state ---
        self.df = None
        self.selected_stream = "All"
        self.selected_job_title = "All"

        # EDA objects/results
        self.full_eda = None
        self.full_results = {}
        self.eda = None
        self.results = {}

    def setup_page_config(self):
        st.set_page_config(
            page_title="Job Market Analytics Dashboard",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded",
        )

    def load_data_and_analysis(self) -> bool:
        """
        Load data, compute full-dataset EDA (once),
        then compute filtered EDA based on current sidebar selections.
        """
        try:
            # Load raw data once
            if self.df is None:
                self.df = pd.read_csv(PROCESSED_DATA_PATH)

            # --- FULL DATA EDA (global views like full stream distribution) ---
            if not self.full_results:  # compute once
                self.full_eda = JobAnalyticsEDA(data=self.df)
                self.full_results = self.full_eda.run_complete_analysis()

            # --- FILTERED DATA ---
            df_filtered = self.df.copy()

            if self.selected_stream != "All":
                df_filtered = df_filtered[df_filtered["Stream"] == self.selected_stream]

            if self.selected_job_title != "All":
                df_filtered = df_filtered[df_filtered["Job Title"] == self.selected_job_title]

            # Guard against empty filter
            if df_filtered.empty:
                st.warning("🚫 No rows match the current filter. Showing no charts.")
                self.eda = None
                self.results = {}
                return False

            # EDA on filtered data
            self.eda = JobAnalyticsEDA(data=df_filtered)
            self.results = self.eda.run_complete_analysis()
            return True

        except Exception as e:
            st.error("❌ Failed to load data or run analysis.")
            st.error(f"Error loading data: {e}")
            self.eda = None
            self.results = {}
            return False

    def create_overview_metrics(self):
        """Create overview metrics cards for the *filtered* data."""
        if not self.results or self.eda is None:
            return

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Jobs",
                f"{len(self.eda.df) if self.eda is not None and self.eda.df is not None else 0:,}",
                help="Total number of job postings analyzed (filtered).",
            )

        with col2:
            st.metric(
                "Unique Companies",
                f"{self.eda.df['Company'].nunique():,}" if self.eda is not None and self.eda.df is not None else "0",
                help="Number of unique companies hiring.",
            )

        with col3:
            st.metric(
                "Job Streams",
                f"{self.eda.df['Stream'].nunique():,}" if self.eda is not None and self.eda.df is not None else "0",
                help="Number of different job categories.",
            )

        with col4:
            quality_score = self.results["quality_metrics"].get("completeness", 0)
            st.metric(
                "Data Quality",
                f"{quality_score:.1f}%",
                help="Overall data completeness score.",
            )

    def create_stream_analysis_charts(self):
        """
        When stream filter == All: show Stream distribution (full dataset).
        When a stream is selected: show role distribution within that stream (filtered dataset).
        """
        st.subheader("🎯 Job Stream / Role Analysis")

        if self.selected_stream == "All":
            # Use FULL dataset for Stream distribution
            stream_data = self.full_results["stream_data"]
            names = stream_data["streams"][:10]
            values = stream_data["counts"][:10]
            pie_title = "Job Distribution by Stream (Top 10)"
            bar_title = "Job Count by Stream (Top 10)"
            y_label = "Job Stream"
        else:
            # Use FILTERED dataset for Role distribution
            # Build role counts directly from filtered DF to reflect user selection
            if self.eda is not None and self.eda.df is not None:
                role_counts = (
                    self.eda.df["Job Title"]
                    .value_counts()
                    .head(10)
                    .reset_index()
                )
                role_counts.columns = ["Job Title", "Count"]
                names = role_counts["Job Title"]
                values = role_counts["Count"]
            else:
                names = []
                values = []
            pie_title = f"{self.selected_stream} – Role Distribution (Top 10)"
            bar_title = f"{self.selected_stream} – Role Count (Top 10)"
            y_label = "Job Title"

        col1, col2 = st.columns(2)

        with col1:
            fig_pie = px.pie(
                values=values,
                names=names,
                title=pie_title,
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            fig_bar = px.bar(
                x=values,
                y=names,
                orientation="h",
                title=bar_title,
                labels={"x": "Number of Jobs", "y": y_label},
                color=values,
                color_continuous_scale="viridis",
            )
            fig_bar.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_bar, use_container_width=True)

    def create_location_analysis_charts(self):
        """Location charts are always based on the *filtered* dataset."""
        if not self.results:
            return

        st.subheader("🌍 Location Analysis")

        location_data = self.results["location_data"]

        col1, col2 = st.columns(2)

        with col1:
            fig_location = px.bar(
                x=location_data["counts"][:15],
                y=location_data["locations"][:15],
                orientation="h",
                title="Top Hiring Locations",
                labels={"x": "Number of Jobs", "y": "Location"},
                color=location_data["counts"][:15],
                color_continuous_scale="blues",
            )
            fig_location.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_location, use_container_width=True)

        with col2:
            fig_treemap = px.treemap(
                names=location_data["locations"][:30],
                values=location_data["counts"][:30],
                title="Location Distribution (Treemap View)",
            )
            st.plotly_chart(fig_treemap, use_container_width=True)

    def create_skills_analysis_charts(self):
        if not self.results:
            return
        st.subheader("🛠️ Skills Analysis")

        skills_data = self.results["skills_data"]

        col1, col2 = st.columns(2)

        with col1:
            fig_skills = px.bar(
                x=skills_data["counts"][:15],
                y=skills_data["skills"][:15],
                orientation="h",
                title="Most In-Demand Skills (Top 15)",
                labels={"x": "Number of Jobs", "y": "Skill"},
                color=skills_data["counts"][:15],
                color_continuous_scale="reds",
            )
            fig_skills.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_skills, use_container_width=True)

        with col2:
            fig_skills_scatter = px.scatter(
                x=list(range(len(skills_data["skills"][:20]))),
                y=skills_data["counts"][:20],
                text=skills_data["skills"][:20],
                size=skills_data["counts"][:20],
                title="Skills Demand Visualization",
                labels={"x": "Skill Rank", "y": "Job Count"},
            )
            fig_skills_scatter.update_traces(textposition="top center")
            fig_skills_scatter.update_layout(showlegend=False)
            st.plotly_chart(fig_skills_scatter, use_container_width=True)

    def create_company_analysis_charts(self):
        if not self.results:
            return
        st.subheader("🏢 Company Analysis")

        company_data = self.results["company_data"]

        fig_company = px.bar(
            x=company_data["counts"][:25],
            y=company_data["companies"][:25],
            orientation="h",
            title="Top Hiring Companies",
            labels={"x": "Number of Jobs", "y": "Company"},
            color=company_data["counts"][:25],
            color_continuous_scale="greens",
        )
        fig_company.update_layout(yaxis={"categoryorder": "total ascending"}, height=600)
        st.plotly_chart(fig_company, use_container_width=True)

    def create_temporal_analysis_charts(self):
        if not self.results:
            return

        temporal_data = self.results["temporal_data"]
        if not temporal_data or not temporal_data.get("has_dates", False):
            st.info("📅 No temporal data available for trend analysis.")
            return

        st.subheader("📅 Temporal Trends Analysis")
        col1, col2 = st.columns(2)

        with col1:
            if temporal_data["daily_dates"]:
                fig_daily = px.line(
                    x=temporal_data["daily_dates"],
                    y=temporal_data["daily_counts"],
                    title="Daily Job Posting Trends",
                    labels={"x": "Date", "y": "Number of Jobs"},
                )
                st.plotly_chart(fig_daily, use_container_width=True)

        with col2:
            if temporal_data["monthly_periods"]:
                fig_monthly = px.bar(
                    x=temporal_data["monthly_periods"],
                    y=temporal_data["monthly_counts"],
                    title="Monthly Job Posting Trends",
                    labels={"x": "Month", "y": "Number of Jobs"},
                )
                st.plotly_chart(fig_monthly, use_container_width=True)

    def create_data_quality_section(self):
        if not self.results:
            return
        st.subheader("✅ Data Quality Analysis")

        quality_metrics = self.results["quality_metrics"]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Completeness Score",
                f"{quality_metrics.get('completeness', 0):.2f}%",
                help="Percentage of non-missing values in dataset",
            )

        with col2:
            st.metric(
                "Uniqueness Score",
                f"{quality_metrics.get('job_uniqueness', 0):.2f}%",
                help="Percentage of unique job titles",
            )

        with col3:
            st.metric(
                "Consistency Score",
                f"{quality_metrics.get('consistency_score', 0):.2f}%",
                help="Data consistency and formatting score",
            )

    def create_export_options(self):
        if not self.results or self.eda is None:
            st.warning("Nothing to export.")
            return

        st.subheader("💾 Export Options")

        col1, col2, col3 = st.columns(3)

        with col1:
            json_str = json.dumps(self.results, indent=2, default=str)
            st.download_button(
                label="📊 Download Analysis Results (JSON)",
                data=json_str,
                file_name=f"job_analysis_results_{datetime.now():%Y%m%d_%H%M%S}.json",
                mime="application/json",
            )

        with col2:
            if self.eda is not None and self.eda.df is not None:
                csv_data = self.eda.df.to_csv(index=False)
            else:
                csv_data = ""
            st.download_button(
                label="📋 Download Filtered Data (CSV)",
                data=csv_data,
                file_name=f"job_data_filtered_{datetime.now():%Y%m%d_%H%M%S}.csv",
                mime="text/csv",
            )

        with col3:
            report = self.generate_summary_report()
            st.download_button(
                label="📈 Download Summary Report (TXT)",
                data=report,
                file_name=f"job_analysis_summary_{datetime.now():%Y%m%d_%H%M%S}.txt",
                mime="text/plain",
            )

    def generate_summary_report(self) -> str:
        if not self.results or self.eda is None:
            return "No analysis results to summarize."

        stream_data = self.results["stream_data"]
        location_data = self.results["location_data"]
        skills_data = self.results["skills_data"]
        quality_metrics = self.results["quality_metrics"]

        total_jobs = len(self.eda.df) if self.eda is not None and self.eda.df is not None else 0
        unique_companies = self.eda.df['Company'].nunique() if self.eda is not None and self.eda.df is not None else 0
        job_streams = self.eda.df['Stream'].nunique() if self.eda is not None and self.eda.df is not None else 0
        locations = self.eda.df['Location'].nunique() if self.eda is not None and self.eda.df is not None else 0

        report = f"""
JOB MARKET ANALYSIS SUMMARY REPORT
Generated on: {datetime.now():%Y-%m-%d %H:%M:%S}

DATASET OVERVIEW (Filtered Selection):
- Total Jobs Analyzed: {total_jobs:,}
- Unique Companies: {unique_companies:,}
- Job Streams: {job_streams:,}
- Locations: {locations:,}

TOP JOB STREAMS:
"""
        for i, (stream, count) in enumerate(
            zip(stream_data["streams"][:5], stream_data["counts"][:5]), start=1
        ):
            report += f"{i}. {stream}: {count:,} jobs\n"

        report += "\nTOP LOCATIONS:\n"
        for i, (location, count) in enumerate(
            zip(location_data["locations"][:5], location_data["counts"][:5]), start=1
        ):
            report += f"{i}. {location}: {count:,} jobs\n"

        report += "\nTOP SKILLS:\n"
        for i, (skill, count) in enumerate(
            zip(skills_data["skills"][:10], skills_data["counts"][:10]), start=1
        ):
            report += f"{i}. {skill}: {count:,} jobs\n"

        report += f"""
DATA QUALITY METRICS:
- Completeness Score: {quality_metrics.get('completeness', 0):.2f}%
- Uniqueness Score: {quality_metrics.get('job_uniqueness', 0):.2f}%
- Consistency Score: {quality_metrics.get('consistency_score', 0):.2f}%

Report generated by Job Analytics Dashboard
"""
        return report

    def run_dashboard(self):
        """Main dashboard runner."""
        self.setup_page_config()
        st.title("📊 Job Market Analytics Dashboard")
        st.markdown("### Comprehensive Analysis of Job Market Trends and Opportunities")
        
        # Data Disclaimer for Analytics Dashboard
        st.warning("""
        ⚠️ **Sample Data Notice**: This dashboard displays demo job market data for illustration purposes. 
        Company names, job postings, and market statistics are simulated and not representative of real market conditions.
        """)
                # Load raw data for sidebar filters
        try:
            if self.df is None:
                self.df = pd.read_csv(PROCESSED_DATA_PATH)
        except Exception as e:
            st.error("❌ Could not load data.")
            st.error(e)
            st.stop()

        # Sidebar filters
        st.sidebar.title("Navigation")
        st.sidebar.markdown("---")
        st.sidebar.header("🔍 Filter Options")

        # Stream selector
        self.selected_stream = st.sidebar.selectbox(
            "🎯 Select Stream:",
            options=["All"] + sorted(self.df["Stream"].dropna().unique().tolist()),
        )

        # Role selector depends on stream
        if self.selected_stream != "All":
            job_roles = (
                self.df[self.df["Stream"] == self.selected_stream]["Job Title"]
                .dropna()
                .unique()
            )
        else:
            job_roles = self.df["Job Title"].dropna().unique()

        self.selected_job_title = st.sidebar.selectbox(
            "💼 Select Job Title:",
            options=["All"] + sorted(job_roles),
        )

        # Run EDA using current filters
        if not self.load_data_and_analysis():
            st.stop()

        # View selector
        analysis_option = st.sidebar.selectbox(
            "Choose Analysis View:",
            [
                "Overview",
                "Stream Analysis",
                "Location Analysis",
                "Skills Analysis",
                "Company Analysis",
                "Temporal Trends",
                "Data Quality",
                "Export Options",
            ],
        )

        # Overview metrics
        self.create_overview_metrics()
        st.markdown("---")

        # Route view
        if analysis_option == "Overview":
            self.create_stream_analysis_charts()
            self.create_location_analysis_charts()
        elif analysis_option == "Stream Analysis":
            self.create_stream_analysis_charts()
        elif analysis_option == "Location Analysis":
            self.create_location_analysis_charts()
        elif analysis_option == "Skills Analysis":
            self.create_skills_analysis_charts()
        elif analysis_option == "Company Analysis":
            self.create_company_analysis_charts()
        elif analysis_option == "Temporal Trends":
            self.create_temporal_analysis_charts()
        elif analysis_option == "Data Quality":
            self.create_data_quality_section()
        elif analysis_option == "Export Options":
            self.create_export_options()

        # Footer
        st.markdown("---")
        st.markdown("**Powered by Professional Data Analytics Pipeline** | Built with Streamlit & Plotly")

# Script entrypoint
if __name__ == "__main__":
    dashboard = JobAnalyticsDashboard()
    dashboard.run_dashboard()

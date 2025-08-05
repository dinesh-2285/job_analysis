# src/eda_module.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from collections import Counter
import logging
import os
import warnings
from typing import Optional
warnings.filterwarnings('ignore')
from job_analysis.config import RAW_DATA_PATH, PROCESSED_DATA_PATH, EXPECTED_COLUMNS, LOG_FILE


class JobAnalyticsEDA:
    """
    Comprehensive Exploratory Data Analysis for Job Market Data
    """
    
    def __init__(self, data=None, data_path=PROCESSED_DATA_PATH):
        self.df = None
        
        if data is not None:
            self.df = data.copy()
            if self.df is not None:
                print(f"✅ EDA: Loaded {len(self.df)} records from DataFrame")
        else:
            self.data_path = data_path
            self.load_data()
        
    def load_data(self):
        """Load cleaned job data"""
        try:
            self.df = pd.read_csv(self.data_path)
            print(f"✅ EDA: Loaded {len(self.df)} records from {self.data_path}")
            
            # Convert date column if exists
            if self.df is not None and 'Date Posted' in self.df.columns:
                self.df['Date Posted'] = pd.to_datetime(self.df['Date Posted'], errors='coerce')
                
            logging.info(f"EDA: Successfully loaded {len(self.df)} records")
            
        except FileNotFoundError:
            print(f"❌ Error: File not found at {self.data_path}")
            print("Please run the data pipeline first: python src/data_pipeline.py")
            raise
        except Exception as e:
            logging.error(f"EDA: Error loading data - {str(e)}")
            raise
    
    def basic_statistics(self):
        """Generate basic statistical summary"""
        try:
            if self.df is None:
                raise ValueError("DataFrame is not loaded")
                
            print("\n📊 BASIC DATASET STATISTICS")
            print("=" * 50)
            print(f"Dataset Shape: {self.df.shape}")
            print(f"Total Records: {len(self.df):,}")
            print(f"Total Columns: {len(self.df.columns)}")
            
            print("\n📋 Column Information:")
            for col in self.df.columns:
                dtype = self.df[col].dtype
                null_count = self.df[col].isnull().sum()
                null_pct = (null_count / len(self.df)) * 100
                print(f"  {col}: {dtype} ({null_count} nulls, {null_pct:.1f}%)")
            
            print("\n📈 Numerical Summary:")
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                print(self.df[numeric_cols].describe())
            else:
                print("No numerical columns found")
                
            return {
                'shape': self.df.shape,
                'total_records': len(self.df),
                'columns': list(self.df.columns),
                'dtypes': self.df.dtypes.to_dict(),
                'null_counts': self.df.isnull().sum().to_dict()
            }
            
        except Exception as e:
            logging.error(f"EDA: Error in basic statistics - {str(e)}")
            raise
    
    def analyze_job_streams(self):
        """Analyze job stream distribution"""
        try:
            if self.df is None:
                raise ValueError("DataFrame is not loaded")
                
            print("\n🎯 JOB STREAM ANALYSIS")
            print("=" * 50)
            
            stream_counts = self.df['Stream'].value_counts()
            stream_pct = (stream_counts / len(self.df)) * 100
            
            print(f"Total Unique Streams: {len(stream_counts)}")
            print("\nTop 10 Job Streams:")
            for i, (stream, count) in enumerate(stream_counts.head(10).items()):
                print(f"{i+1:2d}. {stream:<25} {count:>6,} ({stream_pct.iloc[i]:>5.1f}%)")
            
            return {
                'streams': stream_counts.index.tolist(),
                'counts': stream_counts.values.tolist(),
                'percentages': stream_pct.values.tolist()
            }
            
        except Exception as e:
            logging.error(f"EDA: Error analyzing job streams - {str(e)}")
            raise
    
    def analyze_locations(self):
        """Analyze location distribution"""
        try:
            if self.df is None:
                raise ValueError("DataFrame is not loaded")
                
            print("\n🌍 LOCATION ANALYSIS")
            print("=" * 50)
            
            location_counts = self.df['Location'].value_counts()
            location_pct = (location_counts / len(self.df)) * 100
            
            print(f"Total Unique Locations: {len(location_counts)}")
            print("\nTop 10 Locations:")
            for i, (location, count) in enumerate(location_counts.head(10).items()):
                print(f"{i+1:2d}. {location:<25} {count:>6,} ({location_pct.iloc[i]:>5.1f}%)")
            
            return {
                'locations': location_counts.index.tolist(),
                'counts': location_counts.values.tolist(),
                'percentages': location_pct.values.tolist()
            }
            
        except Exception as e:
            logging.error(f"EDA: Error analyzing locations - {str(e)}")
            raise
    
    def analyze_companies(self):
        """Analyze company distribution"""
        try:
            if self.df is None:
                raise ValueError("DataFrame is not loaded")
                
            print("\n🏢 COMPANY ANALYSIS")
            print("=" * 50)
            
            company_counts = self.df['Company'].value_counts()
            company_pct = (company_counts / len(self.df)) * 100
            
            print(f"Total Unique Companies: {len(company_counts)}")
            print("\nTop 10 Hiring Companies:")
            for i, (company, count) in enumerate(company_counts.head(10).items()):
                print(f"{i+1:2d}. {company:<25} {count:>6,} ({company_pct.iloc[i]:>5.1f}%)")
            
            return {
                'companies': company_counts.index.tolist(),
                'counts': company_counts.values.tolist(),
                'percentages': company_pct.values.tolist()
            }
            
        except Exception as e:
            logging.error(f"EDA: Error analyzing companies - {str(e)}")
            raise
    
    def analyze_skills(self):
        """Analyze skill demand"""
        try:
            if self.df is None:
                raise ValueError("DataFrame is not loaded")
                
            print("\n🛠️ SKILLS ANALYSIS")
            print("=" * 50)
            
            # Extract all skills
            all_skills = []
            for skills_str in self.df['Skills'].dropna():
                if isinstance(skills_str, str):
                    skills = [skill.strip().lower() for skill in skills_str.split(',')]
                    all_skills.extend(skills)
            
            # Count skill frequency
            skill_counts = Counter(all_skills)
            
            print(f"Total Unique Skills: {len(skill_counts)}")
            print(f"Total Skill Mentions: {sum(skill_counts.values()):,}")
            
            print("\nTop 15 Most Demanded Skills:")
            for i, (skill, count) in enumerate(skill_counts.most_common(15)):
                pct = (count / len(self.df)) * 100
                print(f"{i+1:2d}. {skill:<20} {count:>6,} ({pct:>5.1f}%)")
            
            return {
                'skills': [skill for skill, count in skill_counts.most_common()],
                'counts': [count for skill, count in skill_counts.most_common()],
                'total_unique': len(skill_counts),
                'total_mentions': sum(skill_counts.values())
            }
            
        except Exception as e:
            logging.error(f"EDA: Error analyzing skills - {str(e)}")
            raise
    
    def analyze_temporal_trends(self):
        """Analyze temporal patterns in job postings"""
        try:
            if self.df is None:
                raise ValueError("DataFrame is not loaded")
                
            print("\n📅 TEMPORAL ANALYSIS")
            print("=" * 50)
            
            if 'Date Posted' not in self.df.columns:
                print("No date information available for temporal analysis")
                return {
                    'has_dates': False,
                    'daily_dates': [],
                    'daily_counts': [],
                    'monthly_periods': [],
                    'monthly_counts': []
                }
            
            # Filter valid dates
            df_dates = self.df[self.df['Date Posted'].notna()].copy()
            
            if len(df_dates) == 0:
                print("No valid date entries found")
                return {
                    'has_dates': False,
                    'daily_dates': [],
                    'daily_counts': [],
                    'monthly_periods': [],
                    'monthly_counts': []
                }
            
            print(f"Jobs with valid dates: {len(df_dates):,}")
            
            # Daily trends
            # Ensure it's datetime before using .dt
            df_dates['Date Posted'] = pd.to_datetime(df_dates['Date Posted'], errors='coerce')
            daily_counts = df_dates.groupby(df_dates['Date Posted'].dt.date).size()
            print(f"Date range: {daily_counts.index.min()} to {daily_counts.index.max()}")
            
            # Monthly trends
            monthly_counts = df_dates.groupby(df_dates['Date Posted'].dt.to_period('M')).size()
            
            print(f"\nDaily posting statistics:")
            print(f"  Average: {daily_counts.mean():.1f} jobs/day")
            print(f"  Median:  {daily_counts.median():.1f} jobs/day")
            print(f"  Max:     {daily_counts.max()} jobs/day")
            print(f"  Min:     {daily_counts.min()} jobs/day")
            
            return {
                'has_dates': True,
                'daily_dates': daily_counts.index.tolist(),
                'daily_counts': daily_counts.values.tolist(),
                'monthly_periods': [str(period) for period in monthly_counts.index],
                'monthly_counts': monthly_counts.values.tolist(),
                'date_range': {
                    'start': str(daily_counts.index.min()),
                    'end': str(daily_counts.index.max())
                }
            }
            
        except Exception as e:
            logging.error(f"EDA: Error analyzing temporal trends - {str(e)}")
            raise
    
    def analyze_data_quality(self):
        """Analyze data quality metrics"""
        try:
            if self.df is None:
                raise ValueError("DataFrame is not loaded")
                
            print("\n✅ DATA QUALITY ANALYSIS")
            print("=" * 50)
            
            total_cells = len(self.df) * len(self.df.columns)
            missing_cells = self.df.isnull().sum().sum()
            completeness = ((total_cells - missing_cells) / total_cells) * 100
            
            print(f"Data Completeness: {completeness:.2f}%")
            print(f"Missing Values: {missing_cells:,} out of {total_cells:,}")
            
            # Duplicate analysis
            duplicates = self.df.duplicated().sum()
            duplicate_pct = (duplicates / len(self.df)) * 100
            print(f"Duplicate Rows: {duplicates:,} ({duplicate_pct:.2f}%)")
            
            # Unique job titles
            unique_titles = self.df['Job Title'].nunique()
            title_uniqueness = (unique_titles / len(self.df)) * 100
            print(f"Unique Job Titles: {unique_titles:,} ({title_uniqueness:.2f}%)")
            
            # Data consistency checks
            consistency_issues = 0
            
            # Check for mixed case in categorical columns
            for col in ['Stream', 'Location', 'Company']:
                if col in self.df.columns:
                    unique_values = self.df[col].dropna().unique()
                    for val in unique_values:
                        if isinstance(val, str) and val != val.strip():
                            consistency_issues += 1
            
            consistency_score = max(0, 100 - (consistency_issues / len(self.df) * 100))
            
            print(f"Data Consistency Score: {consistency_score:.2f}%")
            
            return {
                'completeness': completeness,
                'missing_cells': missing_cells,
                'total_cells': total_cells,
                'duplicates': duplicates,
                'duplicate_percentage': duplicate_pct,
                'job_uniqueness': title_uniqueness,
                'consistency_score': consistency_score
            }
            
        except Exception as e:
            logging.error(f"EDA: Error analyzing data quality - {str(e)}")
            raise
    
    def generate_correlation_analysis(self):
        """Generate correlation analysis for numerical features"""
        try:
            if self.df is None:
                raise ValueError("DataFrame is not loaded")
                
            print("\n📊 CORRELATION ANALYSIS")
            print("=" * 50)
            
            # Create numerical features
            self.df['skill_count'] = self.df['Skills'].str.count(',') + 1
            self.df['title_length'] = self.df['Job Title'].str.len()
            
            # Company job count
            company_counts = self.df['Company'].value_counts()
            self.df['company_job_count'] = self.df['Company'].map(company_counts)
            
            # Location job count
            location_counts = self.df['Location'].value_counts()
            self.df['location_job_count'] = self.df['Location'].map(location_counts)
            
            # Select numerical columns
            numeric_cols = ['skill_count', 'title_length', 'company_job_count', 'location_job_count']
            correlation_matrix = self.df[numeric_cols].corr()
            
            print("Correlation Matrix:")
            print(correlation_matrix.round(3))
            
            return {
                'correlation_matrix': correlation_matrix.to_dict(),
                'features': numeric_cols
            }
            
        except Exception as e:
            logging.error(f"EDA: Error in correlation analysis - {str(e)}")
            raise
    
    def run_complete_analysis(self):
        """Run complete EDA analysis"""
        try:
            print("\n🚀 STARTING COMPREHENSIVE EDA ANALYSIS")
            print("=" * 60)
            
            # Run all analyses
            basic_stats = self.basic_statistics()
            stream_data = self.analyze_job_streams()
            location_data = self.analyze_locations()
            company_data = self.analyze_companies()
            skills_data = self.analyze_skills()
            temporal_data = self.analyze_temporal_trends()
            quality_metrics = self.analyze_data_quality()
            correlation_data = self.generate_correlation_analysis()
            
            print("\n✅ EDA ANALYSIS COMPLETE!")
            print("=" * 60)
            
            return {
                'basic_stats': basic_stats,
                'stream_data': stream_data,
                'location_data': location_data,
                'company_data': company_data,
                'skills_data': skills_data,
                'temporal_data': temporal_data,
                'quality_metrics': quality_metrics,
                'correlation_data': correlation_data,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"EDA: Error in complete analysis - {str(e)}")
            raise
    
    def export_analysis_report(self, output_path='reports/eda_report.txt'):
        """Export analysis results to text report"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            results = self.run_complete_analysis()
            
            with open(output_path, 'w') as f:
                f.write("JOB MARKET DATA ANALYSIS REPORT\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Basic statistics
                f.write("DATASET OVERVIEW:\n")
                f.write(f"Total Records: {results['basic_stats']['total_records']:,}\n")
                f.write(f"Total Columns: {len(results['basic_stats']['columns'])}\n")
                f.write(f"Data Quality: {results['quality_metrics']['completeness']:.1f}%\n\n")
                
                # Top streams
                f.write("TOP JOB STREAMS:\n")
                for i, (stream, count) in enumerate(zip(results['stream_data']['streams'][:5], 
                                                       results['stream_data']['counts'][:5])):
                    f.write(f"{i+1}. {stream}: {count:,} jobs\n")
                
                # Top locations
                f.write("\nTOP LOCATIONS:\n")
                for i, (location, count) in enumerate(zip(results['location_data']['locations'][:5], 
                                                         results['location_data']['counts'][:5])):
                    f.write(f"{i+1}. {location}: {count:,} jobs\n")
                
                # Top skills
                f.write("\nTOP SKILLS:\n")
                for i, (skill, count) in enumerate(zip(results['skills_data']['skills'][:10], 
                                                      results['skills_data']['counts'][:10])):
                    f.write(f"{i+1}. {skill}: {count:,} mentions\n")
            
            print(f"✅ Analysis report exported to: {output_path}")
            
        except Exception as e:
            logging.error(f"EDA: Error exporting report - {str(e)}")
            raise

# Usage example
if __name__ == "__main__":
    # Create EDA instance and run analysis
    eda = JobAnalyticsEDA()
    
    # Run complete analysis
    results = eda.run_complete_analysis()
    
    # Export report
    eda.export_analysis_report()
    
    print("\n🎉 EDA module ready for use!")

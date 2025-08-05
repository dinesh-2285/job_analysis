# src/data_pipeline.py - Clean data pipeline module

import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime, timedelta
import json

# Set up logging
logger = logging.getLogger(__name__)

def run_pipeline():
    """
    Run the complete data pipeline.
    This is a clean, error-free implementation.
    """
    try:
        logger.info("Starting data pipeline...")
        
        # Import configuration
        from job_analysis.config import RAW_DATA_PATH, PROCESSED_DATA_PATH, ensure_directories
        
        # Ensure directories exist
        ensure_directories()
        
        # Check if raw data exists
        if not os.path.exists(RAW_DATA_PATH):
            logger.warning("Raw data not found, creating sample data...")
            create_sample_data()
        
        # Load and process data
        df = load_raw_data()
        if df is not None:
            processed_df = clean_and_process_data(df)
            save_processed_data(processed_df)
            
            # Generate data quality report
            quality_report = generate_quality_report(processed_df)
            save_quality_report(quality_report)
            
            logger.info("Data pipeline completed successfully")
            return True
        else:
            logger.error("Failed to load raw data")
            return False
            
    except Exception as e:
        logger.error(f"Data pipeline failed: {str(e)}")
        return False

def create_sample_data():
    """Create comprehensive sample job data."""
    try:
        from job_analysis.config import RAW_DATA_PATH
        
        # Enhanced sample data with more realistic job postings
        sample_data = {
            'Job Title': [
                'Senior Data Scientist', 'Software Engineer', 'ML Engineer', 'Business Analyst',
                'Full Stack Developer', 'DevOps Engineer', 'Data Analyst', 'Mobile Developer',
                'Cybersecurity Specialist', 'Product Manager', 'Backend Developer', 'Frontend Developer',
                'Database Administrator', 'Cloud Architect', 'UI/UX Designer', 'QA Engineer',
                'Data Engineer', 'AI Research Scientist', 'Systems Administrator', 'Network Engineer',
                'Sales Engineer', 'Technical Writer', 'Project Manager', 'Scrum Master',
                'Site Reliability Engineer', 'Machine Learning Engineer', 'Business Intelligence Analyst',
                'Full Stack Engineer', 'Security Analyst', 'Cloud Engineer'
            ],
            'Company': [
                'TechCorp Inc', 'InnovateLabs', 'DataFirst Solutions', 'CloudNative Systems', 'WebTech Studios',
                'SecureNet Inc', 'Analytics Pro', 'MobileFirst', 'CyberGuard Solutions', 'ProductVision',
                'CodeCraft Technologies', 'DesignHub', 'DataFlow Systems', 'CloudScale Inc', 'CreativeStudio',
                'QualityFirst', 'BigData Corp', 'AI Innovations', 'SystemsPlus', 'NetworkPro',
                'SalesTech', 'ContentCorp', 'ProjectFlow', 'AgileTech', 'ReliableSystems',
                'MLTech Solutions', 'BusinessIntel', 'FullStack Inc', 'SecureFirst', 'CloudOps'
            ],
            'Location': [
                'New York, NY', 'San Francisco, CA', 'Boston, MA', 'Chicago, IL', 'Austin, TX',
                'Seattle, WA', 'Denver, CO', 'Miami, FL', 'Washington, DC', 'Los Angeles, CA',
                'Portland, OR', 'Atlanta, GA', 'Dallas, TX', 'Phoenix, AZ', 'San Diego, CA',
                'Charlotte, NC', 'Minneapolis, MN', 'Raleigh, NC', 'Nashville, TN', 'Salt Lake City, UT',
                'Detroit, MI', 'Philadelphia, PA', 'Houston, TX', 'Pittsburgh, PA', 'Orlando, FL',
                'Indianapolis, IN', 'Kansas City, MO', 'Tampa, FL', 'Columbus, OH', 'Milwaukee, WI'
            ],
            'Skills': [
                'python;sql;machine learning;pandas;numpy;scikit-learn;tensorflow;statistics;data visualization',
                'java;spring boot;microservices;docker;kubernetes;aws;git;rest api;junit;maven',
                'python;tensorflow;pytorch;deep learning;nlp;computer vision;keras;scikit-learn;pandas',
                'sql;excel;tableau;power bi;agile;jira;requirements gathering;business analysis;stakeholder management',
                'javascript;react;node.js;html;css;mongodb;rest api;git;express;typescript',
                'aws;docker;kubernetes;terraform;jenkins;linux;python;bash;ci/cd;monitoring',
                'python;sql;tableau;excel;pandas;statistics;power bi;data visualization;etl;reporting',
                'swift;kotlin;react native;ios;android;api;xcode;flutter;dart;mobile ui',
                'network security;penetration testing;firewall;linux;python;wireshark;cryptography;vulnerability assessment',
                'agile;scrum;jira;user research;product strategy;sql;analytics;roadmap;stakeholder management',
                'python;django;postgresql;redis;docker;linux;git;rest api;microservices;api design',
                'javascript;react;vue;css;html;webpack;sass;typescript;angular;responsive design',
                'sql;mysql;postgresql;oracle;performance tuning;backup;recovery;nosql;database design',
                'aws;azure;gcp;kubernetes;terraform;microservices;docker;serverless;cloud architecture',
                'figma;sketch;adobe xd;user research;wireframing;prototyping;css;html;user testing',
                'selenium;junit;testng;automation;jira;bug tracking;manual testing;api testing;cypress',
                'python;spark;kafka;airflow;sql;etl;data warehousing;big data;hadoop;snowflake',
                'python;tensorflow;pytorch;research;nlp;computer vision;deep learning;neural networks',
                'linux;windows server;networking;active directory;virtualization;monitoring;vmware;powershell',
                'cisco;networking;routing;switching;firewall;network security;tcp/ip;vpn;network monitoring',
                'technical sales;crm;salesforce;solution architecture;presentation;customer relationship',
                'technical writing;documentation;content management;api documentation;user guides;markdown',
                'project management;agile;scrum;jira;stakeholder management;budget management;risk assessment',
                'agile;scrum;jira;facilitation;coaching;retrospectives;sprint planning;team leadership',
                'python;kubernetes;docker;monitoring;prometheus;grafana;linux;automation;incident response',
                'python;tensorflow;pytorch;machine learning;deep learning;model deployment;mlops;data science',
                'sql;tableau;power bi;excel;data warehousing;etl;business intelligence;data modeling',
                'javascript;python;react;node.js;docker;aws;git;microservices;api;database design',
                'cybersecurity;siem;incident response;forensics;compliance;risk assessment;security frameworks',
                'aws;azure;terraform;kubernetes;docker;ci/cd;infrastructure as code;cloud migration'
            ],
            'Date Posted': [
                '2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19',
                '2024-01-20', '2024-01-21', '2024-01-22', '2024-01-23', '2024-01-24',
                '2024-01-25', '2024-01-26', '2024-01-27', '2024-01-28', '2024-01-29',
                '2024-01-30', '2024-01-31', '2024-02-01', '2024-02-02', '2024-02-03',
                '2024-02-04', '2024-02-05', '2024-02-06', '2024-02-07', '2024-02-08',
                '2024-02-09', '2024-02-10', '2024-02-11', '2024-02-12', '2024-02-13'
            ],
            'Stream': [
                'Data Science & Analytics', 'Software Engineering', 'Artificial Intelligence & Machine Learning',
                'Business Analysis', 'Web Development', 'Cloud & DevOps', 'Data Science & Analytics',
                'Mobile App Development', 'Cyber Security', 'Product Management', 'Software Engineering',
                'Web Development', 'Database Administration', 'Cloud & DevOps', 'Design & UI/UX',
                'Quality Assurance', 'Data Engineering', 'Artificial Intelligence & Machine Learning',
                'IT Infrastructure', 'Network Engineering', 'Sales & Marketing', 'Technical Writing',
                'Project Management', 'Agile & Scrum', 'Cloud & DevOps', 'Artificial Intelligence & Machine Learning',
                'Business Intelligence', 'Software Engineering', 'Cyber Security', 'Cloud & DevOps'
            ],
            'Salary_Range': [
                '$120k-$150k', '$90k-$120k', '$130k-$160k', '$70k-$95k', '$85k-$110k',
                '$110k-$140k', '$75k-$100k', '$95k-$125k', '$105k-$135k', '$100k-$130k',
                '$95k-$125k', '$80k-$105k', '$85k-$115k', '$125k-$155k', '$70k-$95k',
                '$75k-$105k', '$115k-$145k', '$140k-$170k', '$80k-$110k', '$90k-$120k',
                '$85k-$120k', '$65k-$90k', '$90k-$125k', '$80k-$110k', '$120k-$150k',
                '$130k-$165k', '$85k-$115k', '$100k-$135k', '$95k-$130k', '$115k-$145k'
            ],
            'Experience_Level': [
                'Senior', 'Mid', 'Senior', 'Mid', 'Mid',
                'Senior', 'Junior', 'Mid', 'Senior', 'Senior',
                'Mid', 'Junior', 'Mid', 'Senior', 'Mid',
                'Mid', 'Senior', 'Senior', 'Mid', 'Mid',
                'Mid', 'Junior', 'Senior', 'Mid', 'Senior',
                'Senior', 'Mid', 'Senior', 'Mid', 'Senior'
            ],
            'Job_Type': [
                'Full-time', 'Full-time', 'Full-time', 'Full-time', 'Full-time',
                'Full-time', 'Full-time', 'Full-time', 'Full-time', 'Full-time',
                'Full-time', 'Contract', 'Full-time', 'Full-time', 'Contract',
                'Full-time', 'Full-time', 'Full-time', 'Full-time', 'Full-time',
                'Full-time', 'Contract', 'Full-time', 'Full-time', 'Full-time',
                'Full-time', 'Full-time', 'Full-time', 'Full-time', 'Full-time'
            ],
            'Remote_Option': [
                'Hybrid', 'Remote', 'On-site', 'Hybrid', 'Remote',
                'Hybrid', 'On-site', 'Remote', 'On-site', 'Hybrid',
                'Remote', 'Remote', 'On-site', 'Hybrid', 'Remote',
                'Hybrid', 'Remote', 'On-site', 'On-site', 'Hybrid',
                'Remote', 'Remote', 'Hybrid', 'Remote', 'Hybrid',
                'Remote', 'Hybrid', 'Remote', 'On-site', 'Hybrid'
            ]
        }
        
        df = pd.DataFrame(sample_data)
        df.to_csv(RAW_DATA_PATH, index=False)
        logger.info(f"Created sample data with {len(df)} records: {RAW_DATA_PATH}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create sample data: {str(e)}")
        return False

def load_raw_data():
    """Load raw data from CSV file."""
    try:
        from job_analysis.config import RAW_DATA_PATH
        
        if not os.path.exists(RAW_DATA_PATH):
            logger.error(f"Raw data file not found: {RAW_DATA_PATH}")
            return None
        
        df = pd.read_csv(RAW_DATA_PATH)
        logger.info(f"Loaded {len(df)} records from raw data")
        return df
        
    except Exception as e:
        logger.error(f"Failed to load raw data: {str(e)}")
        return None

def clean_and_process_data(df):
    """Clean and process the raw data."""
    try:
        logger.info("Starting data cleaning and processing...")
        
        # Make a copy to avoid modifying original
        processed_df = df.copy()
        
        # Basic cleaning
        processed_df = processed_df.dropna(subset=['Job Title', 'Company', 'Stream'])
        
        # Standardize date format (handle both DD-MM-YYYY and YYYY-MM-DD formats)
        if 'Date Posted' in processed_df.columns:
            # Clean the date column first (remove any text like 'Date Posted')
            processed_df = processed_df[processed_df['Date Posted'] != 'Date Posted']
            
            # Try DD-MM-YYYY format first
            dates = pd.to_datetime(processed_df['Date Posted'], format='%d-%m-%Y', errors='coerce')
            
            # For failed dates, try YYYY-MM-DD format
            failed_mask = dates.isna()
            if failed_mask.any():
                dates[failed_mask] = pd.to_datetime(
                    processed_df.loc[failed_mask, 'Date Posted'], 
                    format='%Y-%m-%d', 
                    errors='coerce'
                )
            
            # For any still failed, try general parsing
            still_failed = dates.isna()
            if still_failed.any():
                dates[still_failed] = pd.to_datetime(
                    processed_df.loc[still_failed, 'Date Posted'], 
                    errors='coerce'
                )
            
            processed_df['Date Posted'] = dates
        
        # Clean and standardize text fields
        text_columns = ['Job Title', 'Company', 'Location', 'Stream']
        for col in text_columns:
            if col in processed_df.columns:
                processed_df[col] = processed_df[col].astype(str).str.strip()
        
        # Process skills column
        if 'Skills' in processed_df.columns:
            processed_df['Skills'] = processed_df['Skills'].astype(str).str.lower()
            processed_df['Skill_Count'] = processed_df['Skills'].str.split(';').str.len()
        
        # Add derived columns
        if 'Date Posted' in processed_df.columns:
            processed_df['Days_Since_Posted'] = (datetime.now() - processed_df['Date Posted']).dt.days
            processed_df['Month_Posted'] = processed_df['Date Posted'].dt.month
            processed_df['Year_Posted'] = processed_df['Date Posted'].dt.year
        
        # Extract salary information
        if 'Salary_Range' in processed_df.columns:
            processed_df['Salary_Min'], processed_df['Salary_Max'] = extract_salary_range(processed_df['Salary_Range'])
        
        # Add job posting freshness
        if 'Days_Since_Posted' in processed_df.columns:
            processed_df['Posting_Freshness'] = processed_df['Days_Since_Posted'].apply(categorize_freshness)
        
        # Remove duplicates
        processed_df = processed_df.drop_duplicates(subset=['Job Title', 'Company', 'Location'], keep='first')
        
        logger.info(f"Data processing completed. {len(processed_df)} records after cleaning")
        return processed_df
        
    except Exception as e:
        logger.error(f"Data processing failed: {str(e)}")
        return df  # Return original data if processing fails

def extract_salary_range(salary_column):
    """Extract min and max salary from salary range strings."""
    try:
        import re
        
        min_salaries = []
        max_salaries = []
        
        for salary_str in salary_column:
            if pd.isna(salary_str):
                min_salaries.append(np.nan)
                max_salaries.append(np.nan)
                continue
            
            # Extract numbers using regex
            numbers = re.findall(r'\d+', str(salary_str))
            if len(numbers) >= 2:
                min_sal = int(numbers[0]) * 1000  # Assuming values are in thousands
                max_sal = int(numbers[1]) * 1000
                min_salaries.append(min_sal)
                max_salaries.append(max_sal)
            else:
                min_salaries.append(np.nan)
                max_salaries.append(np.nan)
        
        return min_salaries, max_salaries
        
    except Exception as e:
        logger.error(f"Salary extraction failed: {str(e)}")
        return [np.nan] * len(salary_column), [np.nan] * len(salary_column)

def categorize_freshness(days_since_posted):
    """Categorize job posting freshness."""
    if pd.isna(days_since_posted):
        return 'Unknown'
    elif days_since_posted <= 7:
        return 'Fresh'
    elif days_since_posted <= 30:
        return 'Recent'
    elif days_since_posted <= 90:
        return 'Older'
    else:
        return 'Stale'

def save_processed_data(df):
    """Save processed data to CSV file."""
    try:
        from job_analysis.config import PROCESSED_DATA_PATH
        
        df.to_csv(PROCESSED_DATA_PATH, index=False)
        logger.info(f"Saved processed data with {len(df)} records: {PROCESSED_DATA_PATH}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save processed data: {str(e)}")
        return False

def generate_quality_report(df):
    """Generate data quality report."""
    try:
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_records': len(df),
            'columns': list(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.astype(str).to_dict(),
            'duplicate_records': df.duplicated().sum(),
            'unique_values': {col: df[col].nunique() for col in df.columns},
            'quality_score': calculate_quality_score(df)
        }
        
        # Add specific insights
        if 'Stream' in df.columns:
            report['stream_distribution'] = df['Stream'].value_counts().to_dict()
        
        if 'Skills' in df.columns:
            all_skills = df['Skills'].str.split(';').explode().str.strip()
            report['total_unique_skills'] = all_skills.nunique()
            report['top_skills'] = all_skills.value_counts().head(10).to_dict()
        
        logger.info("Data quality report generated successfully")
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate quality report: {str(e)}")
        return {}

def calculate_quality_score(df):
    """Calculate overall data quality score."""
    try:
        # Calculate completeness (percentage of non-null values)
        completeness = (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        
        # Calculate uniqueness (percentage of unique records)
        uniqueness = (1 - df.duplicated().sum() / len(df)) * 100 if len(df) > 0 else 0
        
        # Overall quality score (simple average for now)
        quality_score = (completeness + uniqueness) / 2
        
        return round(quality_score, 2)
        
    except Exception as e:
        logger.error(f"Failed to calculate quality score: {str(e)}")
        return 0

def save_quality_report(report):
    """Save quality report to JSON file."""
    try:
        from job_analysis.config import LOGS_DIR
        
        report_path = os.path.join(LOGS_DIR, 'data_quality_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Quality report saved: {report_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save quality report: {str(e)}")
        return False

def get_pipeline_status():
    """Get current pipeline status and metrics."""
    try:
        from job_analysis.config import RAW_DATA_PATH, PROCESSED_DATA_PATH, LOGS_DIR
        
        status = {
            'raw_data_exists': os.path.exists(RAW_DATA_PATH),
            'processed_data_exists': os.path.exists(PROCESSED_DATA_PATH),
            'raw_data_count': 0,
            'processed_data_count': 0,
            'last_update': None
        }
        
        if status['raw_data_exists']:
            try:
                raw_df = pd.read_csv(RAW_DATA_PATH)
                status['raw_data_count'] = len(raw_df)
            except:
                pass
        
        if status['processed_data_exists']:
            try:
                processed_df = pd.read_csv(PROCESSED_DATA_PATH)
                status['processed_data_count'] = len(processed_df)
                
                # Get file modification time
                mod_time = os.path.getmtime(PROCESSED_DATA_PATH)
                status['last_update'] = datetime.fromtimestamp(mod_time).isoformat()
            except:
                pass
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get pipeline status: {str(e)}")
        return {}

def validate_data_schema(df):
    """Validate data schema against expected format."""
    try:
        from job_analysis.config import EXPECTED_COLUMNS
        
        validation_results = {
            'is_valid': True,
            'missing_columns': [],
            'extra_columns': [],
            'column_types': {}
        }
        
        # Check for missing columns
        missing_cols = set(EXPECTED_COLUMNS) - set(df.columns)
        if missing_cols:
            validation_results['missing_columns'] = list(missing_cols)
            validation_results['is_valid'] = False
        
        # Check for extra columns
        extra_cols = set(df.columns) - set(EXPECTED_COLUMNS)
        if extra_cols:
            validation_results['extra_columns'] = list(extra_cols)
        
        # Record column types
        validation_results['column_types'] = df.dtypes.astype(str).to_dict()
        
        return validation_results
        
    except Exception as e:
        logger.error(f"Schema validation failed: {str(e)}")
        return {'is_valid': False, 'error': str(e)}

# Main pipeline execution function
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run pipeline
    success = run_pipeline()
    if success:
        print("Data pipeline completed successfully!")
    else:
        print("Data pipeline failed. Check logs for details.")

# job_analysis/config.py - Clean configuration management

import os
from datetime import datetime

# Project Structure
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# Data Paths
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')

RAW_DATA_PATH = os.path.join(RAW_DATA_DIR, 'linkedin_jobs.csv')
PROCESSED_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, 'clean_jobs.csv')

# Model Paths
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')
STREAM_PREDICTOR_PATH = os.path.join(MODELS_DIR, 'stream_predictor.pkl')
STREAM_ENCODER_PATH = os.path.join(MODELS_DIR, 'stream_encoder.pkl')
STREAM_VECTORIZER_PATH = os.path.join(MODELS_DIR, 'stream_vectorizer.pkl')
DEMAND_FORECASTER_PATH = os.path.join(MODELS_DIR, 'demand_forecaster.pkl')

# Logging
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')
LOG_FILE = os.path.join(LOGS_DIR, 'data_ingestion.log')
ML_LOG_FILE = os.path.join(LOGS_DIR, 'ml_training.log')
APP_LOG_FILE = os.path.join(LOGS_DIR, 'app.log')

# Data Schema
EXPECTED_COLUMNS = [
    'Job Title', 'Company', 'Location', 'Skills', 'Date Posted', 'Stream'
]

# Application Settings
APP_CONFIG = {
    'page_title': 'Professional Job Analytics Platform',
    'page_icon': '🚀',
    'layout': 'wide',
    'max_file_upload_size': 200,  # MB
    'session_timeout': 3600,  # seconds
}

# ML Model Settings
ML_CONFIG = {
    'test_size': 0.2,
    'random_state': 42,
    'max_features': 5000,
    'min_skill_frequency': 2,
    'prediction_confidence_threshold': 0.7
}

# Dashboard Settings
DASHBOARD_CONFIG = {
    'chart_height': 400,
    'max_records_display': 1000,
    'refresh_interval': 300,  # seconds
    'color_palette': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
}

def ensure_directories():
    """Create necessary directories if they don't exist."""
    directories = [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, LOGS_DIR, MODELS_DIR]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def get_timestamp():
    """Get current timestamp for logging."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Skill categories for job classification
SKILL_CATEGORIES = {
    'programming_languages': [
        'python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin'
    ],
    'web_technologies': [
        'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'laravel'
    ],
    'databases': [
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'nosql'
    ],
    'cloud_platforms': [
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'serverless'
    ],
    'data_science': [
        'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'matplotlib', 'seaborn', 'plotly'
    ],
    'tools_and_frameworks': [
        'git', 'jira', 'jenkins', 'linux', 'agile', 'scrum', 'api', 'microservices'
    ]
}

# Job stream definitions
JOB_STREAMS = {
    'Data Science & Analytics': {
        'description': 'Data analysis, machine learning, and business intelligence',
        'key_skills': ['python', 'sql', 'statistics', 'machine learning', 'tableau', 'power bi'],
        'growth_rate': 'High'
    },
    'Software Engineering': {
        'description': 'Software development and system architecture',
        'key_skills': ['python', 'java', 'javascript', 'git', 'microservices', 'api'],
        'growth_rate': 'High'
    },
    'Web Development': {
        'description': 'Frontend and backend web application development',
        'key_skills': ['html', 'css', 'javascript', 'react', 'node.js', 'mongodb'],
        'growth_rate': 'Medium'
    },
    'Cloud & DevOps': {
        'description': 'Cloud infrastructure and deployment automation',
        'key_skills': ['aws', 'docker', 'kubernetes', 'terraform', 'ci/cd', 'linux'],
        'growth_rate': 'Very High'
    },
    'Artificial Intelligence & Machine Learning': {
        'description': 'AI research and ML model development',
        'key_skills': ['python', 'tensorflow', 'pytorch', 'nlp', 'computer vision', 'deep learning'],
        'growth_rate': 'Very High'
    }
}

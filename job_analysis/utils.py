"""
Utility functions for the job analysis application.
"""

import os
import logging
import pandas as pd
from typing import List, Dict, Any, Optional
from .config import *

def setup_logging(log_file: str = APP_LOG_FILE, level: int = logging.INFO):
    """Set up logging configuration."""
    ensure_directories()
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def validate_data_columns(df: pd.DataFrame, required_columns: List[str] = EXPECTED_COLUMNS) -> bool:
    """Validate that DataFrame has required columns."""
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    return True

def load_job_data(file_path: str = RAW_DATA_PATH) -> Optional[pd.DataFrame]:
    """Load job data with error handling."""
    try:
        if not os.path.exists(file_path):
            return None
        
        df = pd.read_csv(file_path)
        validate_data_columns(df)
        return df
    except Exception as e:
        logging.error(f"Error loading data from {file_path}: {str(e)}")
        return None

def save_processed_data(df: pd.DataFrame, file_path: str = PROCESSED_DATA_PATH) -> bool:
    """Save processed data with error handling."""
    try:
        ensure_directories()
        df.to_csv(file_path, index=False)
        logging.info(f"Data saved successfully to {file_path}")
        return True
    except Exception as e:
        logging.error(f"Error saving data to {file_path}: {str(e)}")
        return False

def get_project_info() -> Dict[str, Any]:
    """Get project information and status."""
    return {
        'project_root': PROJECT_ROOT,
        'data_files': {
            'raw_data_exists': os.path.exists(RAW_DATA_PATH),
            'processed_data_exists': os.path.exists(PROCESSED_DATA_PATH),
        },
        'model_files': {
            'stream_predictor_exists': os.path.exists(STREAM_PREDICTOR_PATH),
            'stream_encoder_exists': os.path.exists(STREAM_ENCODER_PATH),
            'stream_vectorizer_exists': os.path.exists(STREAM_VECTORIZER_PATH),
            'demand_forecaster_exists': os.path.exists(DEMAND_FORECASTER_PATH),
        },
        'directories': {
            'data_dir_exists': os.path.exists(DATA_DIR),
            'logs_dir_exists': os.path.exists(LOGS_DIR),
            'models_dir_exists': os.path.exists(MODELS_DIR),
        }
    }

def clean_skill_text(skill_text: str) -> List[str]:
    """Clean and parse skill text."""
    if pd.isna(skill_text) or not skill_text:
        return []
    
    # Split by common separators and clean
    skills = []
    for separator in [';', ',', '|', '\n']:
        if separator in skill_text:
            skills = skill_text.split(separator)
            break
    else:
        skills = [skill_text]
    
    # Clean each skill
    cleaned_skills = []
    for skill in skills:
        skill = skill.strip().lower()
        if skill and len(skill) > 1:
            cleaned_skills.append(skill)
    
    return cleaned_skills

def get_skill_frequency(df: pd.DataFrame, min_frequency: int = ML_CONFIG['min_skill_frequency']) -> Dict[str, int]:
    """Get frequency count of skills in the dataset."""
    all_skills = []
    for skills_text in df['Skills'].dropna():
        all_skills.extend(clean_skill_text(skills_text))
    
    skill_counts = {}
    for skill in all_skills:
        skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    # Filter by minimum frequency
    return {skill: count for skill, count in skill_counts.items() if count >= min_frequency}

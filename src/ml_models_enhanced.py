# src/ml_models_enhanced.py - Clean ML models module

import pandas as pd
import numpy as np
import logging
from collections import Counter
import joblib
import os

# Set up logging
logger = logging.getLogger(__name__)

class JobAnalyticsML:
    """
    Clean and robust ML models for job analytics.
    Self-contained with fallback functionality.
    """
    
    def __init__(self):
        """Initialize ML models."""
        self.models = {}
        self.vectorizers = {}
        self.encoders = {}
        self.is_trained = False
        
        # Try to load existing models
        self.load_models()
    
    def load_models(self):
        """Load pre-trained models if they exist."""
        try:
            from job_analysis.config import MODELS_DIR
            
            model_files = {
                'stream_predictor': os.path.join(MODELS_DIR, 'stream_predictor.pkl'),
                'stream_vectorizer': os.path.join(MODELS_DIR, 'stream_vectorizer.pkl'),
                'stream_encoder': os.path.join(MODELS_DIR, 'stream_encoder.pkl')
            }
            
            loaded_count = 0
            for model_name, file_path in model_files.items():
                if os.path.exists(file_path):
                    try:
                        if 'vectorizer' in model_name:
                            self.vectorizers[model_name] = joblib.load(file_path)
                        elif 'encoder' in model_name:
                            self.encoders[model_name] = joblib.load(file_path)
                        else:
                            self.models[model_name] = joblib.load(file_path)
                        loaded_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to load {model_name}: {str(e)}")
            
            if loaded_count > 0:
                self.is_trained = True
                logger.info(f"Loaded {loaded_count} pre-trained models")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
    
    def run_complete_ml_pipeline(self):
        """Run the complete ML pipeline."""
        try:
            logger.info("Starting ML pipeline...")
            
            # Load data
            df = self.load_data()
            if df is None or df.empty:
                logger.error("No data available for ML training")
                return {'success': False, 'error': 'No data available'}
            
            # Train models
            results = {}
            
            # Train stream prediction model
            stream_accuracy = self.train_stream_predictor(df)
            results['stream_accuracy'] = stream_accuracy
            
            # Train demand forecasting (simple version)
            demand_results = self.train_demand_forecaster(df)
            results.update(demand_results)
            
            # Save models
            self.save_models()
            
            self.is_trained = True
            logger.info("ML pipeline completed successfully")
            
            return {
                'success': True,
                'stream_accuracy': results.get('stream_accuracy', 0),
                'demand_mse': results.get('demand_mse', None),
                'models_trained': len(self.models)
            }
            
        except Exception as e:
            logger.error(f"ML pipeline failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def load_data(self):
        """Load processed data for ML training."""
        try:
            from job_analysis.config import PROCESSED_DATA_PATH
            
            if os.path.exists(PROCESSED_DATA_PATH):
                df = pd.read_csv(PROCESSED_DATA_PATH)
                logger.info(f"Loaded {len(df)} records for ML training")
                return df
            else:
                logger.warning("Processed data not found")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load data: {str(e)}")
            return None
    
    def train_stream_predictor(self, df):
        """Train job stream prediction model."""
        try:
            if 'Skills' not in df.columns or 'Stream' not in df.columns:
                logger.error("Required columns not found for stream prediction")
                return 0
            
            # Import ML libraries with fallback
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                from sklearn.linear_model import LogisticRegression
                from sklearn.model_selection import train_test_split
                from sklearn.metrics import accuracy_score
                from sklearn.preprocessing import LabelEncoder
            except ImportError:
                logger.error("scikit-learn not available")
                return 0
            
            # Prepare data
            X = df['Skills'].fillna('').astype(str)
            y = df['Stream']
            
            # Clean and preprocess skills text
            X = X.str.replace(';', ' ').str.lower()
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Vectorize skills text
            vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            X_train_vec = vectorizer.fit_transform(X_train)
            X_test_vec = vectorizer.transform(X_test)
            
            # Encode labels
            label_encoder = LabelEncoder()
            y_train_encoded = label_encoder.fit_transform(y_train)
            y_test_encoded = label_encoder.transform(y_test)
            
            # Train model
            model = LogisticRegression(random_state=42, max_iter=1000)
            model.fit(X_train_vec, y_train_encoded)
            
            # Evaluate
            y_pred = model.predict(X_test_vec)
            accuracy = accuracy_score(y_test_encoded, y_pred)
            
            # Store models
            self.models['stream_predictor'] = model
            self.vectorizers['stream_vectorizer'] = vectorizer
            self.encoders['stream_encoder'] = label_encoder
            
            logger.info(f"Stream predictor trained with accuracy: {accuracy:.2%}")
            return accuracy
            
        except Exception as e:
            logger.error(f"Stream predictor training failed: {str(e)}")
            return 0
    
    def train_demand_forecaster(self, df):
        """Train simple demand forecasting model."""
        try:
            # Simple demand analysis based on job counts by stream
            if 'Stream' not in df.columns:
                logger.error("Stream column not found for demand forecasting")
                return {'demand_mse': None}
            
            # Count jobs by stream
            stream_counts = df['Stream'].value_counts()
            
            # Simple forecasting: predict next period demand based on current counts
            # This is a simplified version for demonstration
            forecasted_demand = {}
            for stream, count in stream_counts.items():
                # Simple trend: assume 5% growth
                forecasted_demand[stream] = count * 1.05
            
            # Calculate simple MSE (for demonstration)
            actual_values = list(stream_counts.values)
            predicted_values = [forecasted_demand[stream] for stream in stream_counts.index]
            
            mse = np.mean([(a - p) ** 2 for a, p in zip(actual_values, predicted_values)])
            
            # Store demand model (simple dictionary for now)
            self.models['demand_forecaster'] = {
                'current_demand': stream_counts.to_dict(),
                'forecasted_demand': forecasted_demand,
                'growth_rate': 1.05
            }
            
            logger.info(f"Demand forecaster trained with MSE: {mse:.2f}")
            return {'demand_mse': mse, 'forecasted_demand': forecasted_demand}
            
        except Exception as e:
            logger.error(f"Demand forecaster training failed: {str(e)}")
            return {'demand_mse': None}
    
    def predict_stream(self, skills_text):
        """Predict job stream from skills."""
        try:
            if not self.is_trained or 'stream_predictor' not in self.models:
                return None, 0
            
            # Preprocess skills
            skills_cleaned = str(skills_text).replace(';', ' ').lower()
            
            # Vectorize
            vectorizer = self.vectorizers.get('stream_vectorizer')
            if vectorizer is None:
                return None, 0
            
            skills_vec = vectorizer.transform([skills_cleaned])
            
            # Predict
            model = self.models['stream_predictor']
            prediction = model.predict(skills_vec)[0]
            confidence = np.max(model.predict_proba(skills_vec))
            
            # Decode prediction
            encoder = self.encoders.get('stream_encoder')
            if encoder:
                predicted_stream = encoder.inverse_transform([prediction])[0]
                return predicted_stream, confidence
            
            return None, 0
            
        except Exception as e:
            logger.error(f"Stream prediction failed: {str(e)}")
            return None, 0
    
    def get_skill_recommendations(self, target_stream):
        """Get skill recommendations for a target stream."""
        try:
            # Skill mapping for recommendations
            skill_mapping = {
                "Data Science & Analytics": [
                    "python", "sql", "r", "tableau", "power bi", "pandas", "numpy", 
                    "scikit-learn", "statistics", "machine learning", "data visualization"
                ],
                "Software Engineering": [
                    "python", "java", "javascript", "git", "docker", "aws", 
                    "microservices", "api", "database design", "testing"
                ],
                "Web Development": [
                    "html", "css", "javascript", "react", "node.js", "mongodb", 
                    "rest api", "responsive design", "git", "typescript"
                ],
                "Cloud & DevOps": [
                    "aws", "docker", "kubernetes", "terraform", "ci/cd", "linux", 
                    "monitoring", "infrastructure as code", "automation"
                ],
                "Artificial Intelligence & Machine Learning": [
                    "python", "tensorflow", "pytorch", "deep learning", "nlp", 
                    "computer vision", "neural networks", "model deployment"
                ]
            }
            
            recommendations = skill_mapping.get(target_stream, [])
            
            return {
                'target_stream': target_stream,
                'recommended_skills': recommendations[:10],  # Top 10
                'skill_categories': self.categorize_skills(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Skill recommendation failed: {str(e)}")
            return {}
    
    def categorize_skills(self, skills):
        """Categorize skills into different types."""
        categories = {
            'programming': ['python', 'java', 'javascript', 'r', 'sql'],
            'tools': ['git', 'docker', 'kubernetes', 'tableau', 'power bi'],
            'frameworks': ['react', 'tensorflow', 'pytorch', 'django', 'flask'],
            'concepts': ['machine learning', 'deep learning', 'microservices', 'api', 'ci/cd']
        }
        
        categorized = {}
        for category, category_skills in categories.items():
            categorized[category] = [skill for skill in skills if skill in category_skills]
        
        return categorized
    
    def get_demand_forecast(self):
        """Get demand forecast for different job streams."""
        try:
            if 'demand_forecaster' not in self.models:
                return {}
            
            demand_model = self.models['demand_forecaster']
            
            return {
                'current_demand': demand_model.get('current_demand', {}),
                'forecasted_demand': demand_model.get('forecasted_demand', {}),
                'growth_trends': self.calculate_growth_trends(demand_model)
            }
            
        except Exception as e:
            logger.error(f"Demand forecast failed: {str(e)}")
            return {}
    
    def calculate_growth_trends(self, demand_model):
        """Calculate growth trends for job streams."""
        try:
            current = demand_model.get('current_demand', {})
            forecasted = demand_model.get('forecasted_demand', {})
            
            trends = {}
            for stream in current.keys():
                if stream in forecasted:
                    growth_rate = (forecasted[stream] - current[stream]) / current[stream] * 100
                    if growth_rate > 10:
                        trend = 'High Growth'
                    elif growth_rate > 5:
                        trend = 'Moderate Growth'
                    elif growth_rate > 0:
                        trend = 'Slow Growth'
                    else:
                        trend = 'Declining'
                    
                    trends[stream] = {
                        'growth_rate': growth_rate,
                        'trend': trend
                    }
            
            return trends
            
        except Exception as e:
            logger.error(f"Growth trend calculation failed: {str(e)}")
            return {}
    
    def save_models(self):
        """Save trained models to disk."""
        try:
            from job_analysis.config import MODELS_DIR, ensure_directories
            
            ensure_directories()
            
            # Save main models
            for model_name, model in self.models.items():
                file_path = os.path.join(MODELS_DIR, f'{model_name}.pkl')
                joblib.dump(model, file_path)
                logger.info(f"Saved model: {model_name}")
            
            # Save vectorizers
            for vec_name, vectorizer in self.vectorizers.items():
                file_path = os.path.join(MODELS_DIR, f'{vec_name}.pkl')
                joblib.dump(vectorizer, file_path)
                logger.info(f"Saved vectorizer: {vec_name}")
            
            # Save encoders
            for enc_name, encoder in self.encoders.items():
                file_path = os.path.join(MODELS_DIR, f'{enc_name}.pkl')
                joblib.dump(encoder, file_path)
                logger.info(f"Saved encoder: {enc_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save models: {str(e)}")
            return False
    
    def get_model_info(self):
        """Get information about trained models."""
        try:
            info = {
                'is_trained': self.is_trained,
                'models_count': len(self.models),
                'vectorizers_count': len(self.vectorizers),
                'encoders_count': len(self.encoders),
                'available_models': list(self.models.keys()),
                'capabilities': []
            }
            
            # Check capabilities
            if 'stream_predictor' in self.models:
                info['capabilities'].append('Stream Prediction')
            
            if 'demand_forecaster' in self.models:
                info['capabilities'].append('Demand Forecasting')
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get model info: {str(e)}")
            return {}
    
    def analyze_skill_gaps(self, user_skills, target_stream):
        """Analyze skill gaps for a user targeting a specific stream."""
        try:
            # Get recommended skills for target stream
            recommendations = self.get_skill_recommendations(target_stream)
            recommended_skills = set([s.lower() for s in recommendations.get('recommended_skills', [])])
            
            # Parse user skills
            user_skills_set = set([s.strip().lower() for s in str(user_skills).split(',') if s.strip()])
            
            # Calculate gaps
            skill_gaps = {
                'missing_skills': list(recommended_skills - user_skills_set),
                'matching_skills': list(recommended_skills & user_skills_set),
                'extra_skills': list(user_skills_set - recommended_skills),
                'match_percentage': len(recommended_skills & user_skills_set) / len(recommended_skills) * 100 if recommended_skills else 0
            }
            
            # Add priority levels
            skill_gaps['priority_skills'] = skill_gaps['missing_skills'][:5]  # Top 5 missing skills
            
            return skill_gaps
            
        except Exception as e:
            logger.error(f"Skill gap analysis failed: {str(e)}")
            return {}

# Utility functions for ML pipeline
def create_sample_ml_data():
    """Create sample data specifically for ML training if needed."""
    try:
        # This would create more structured data for ML training
        # For now, we'll rely on the main data pipeline
        logger.info("Sample ML data creation not needed - using main pipeline data")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create sample ML data: {str(e)}")
        return False

def validate_ml_requirements():
    """Validate that ML requirements are met."""
    try:
        required_packages = ['pandas', 'numpy', 'scikit-learn', 'joblib']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"Missing ML packages: {missing_packages}")
            return False, missing_packages
        
        return True, []
        
    except Exception as e:
        logger.error(f"ML requirements validation failed: {str(e)}")
        return False, [str(e)]

# Main execution for testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test ML pipeline
    ml_system = JobAnalyticsML()
    results = ml_system.run_complete_ml_pipeline()
    
    if results.get('success'):
        print("ML pipeline completed successfully!")
        print(f"Stream accuracy: {results.get('stream_accuracy', 0):.2%}")
    else:
        print(f"ML pipeline failed: {results.get('error', 'Unknown error')}")

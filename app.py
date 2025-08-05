# app.py

import streamlit as st
from src.dashboard import JobAnalyticsDashboard
from src.resume_interface import ResumeMatchingInterface
from src.data_pipeline import run_pipeline
from src.ml_models_enhanced import JobAnalyticsML
import pandas as pd
from collections import Counter
import re

# --- State Management Initialization ---
if 'ml_model' not in st.session_state:
    st.session_state.ml_model = JobAnalyticsML()
    st.session_state.models_trained = False

def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(
        page_title="Professional Job Analytics Platform",
        page_icon="🚀",
        layout="wide"
    )
    
    st.sidebar.title("🚀 Job Analytics Platform")
    st.sidebar.markdown("---")
    
    main_option = st.sidebar.selectbox(
        "Choose Module:",
        ["🏠 Home", "📊 Analytics Dashboard", "🎯 Resume Matcher", "🤖 ML Models", "⚙️ Data Pipeline"]
    )
    
    if main_option == "🏠 Home":
        st.title("🚀 Professional Job Analytics Platform")
        st.markdown("""
        ### Welcome to the Complete End-to-End Job Analytics Solution!
        
        This platform provides comprehensive job market analysis and intelligent resume matching capabilities.
        
        #### 🌟 Features:
        - **📊 Analytics Dashboard**: Interactive visualizations and market insights.
        - **🎯 AI Resume Matcher**: Advanced resume-to-job matching with NLP.
        - **🤖 ML Models**: Predictive analytics and trend forecasting.
        - **⚙️ Data Pipeline**: Automated data processing and quality checks.
        
        #### 🎯 Choose a module from the sidebar to get started!
        """)
        
        # Data Disclaimer
        st.info("""
        📋 **Data Disclaimer**: This application uses sample/demo job data for demonstration purposes only. 
        The job postings, companies, and salary information are not real and should not be used for actual 
        job search or market analysis decisions.
        """)
        
        # Quick stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Features", "15+")
        with col2:
            st.metric("Data Processing", "Automated")
        with col3:
            st.metric("Match Accuracy", "90%+")
    
    elif main_option == "📊 Analytics Dashboard":
        dashboard = JobAnalyticsDashboard()
        dashboard.run_dashboard()
    
    elif main_option == "🎯 Resume Matcher":
        interface = ResumeMatchingInterface()
        interface.run_interface()
    
    elif main_option == "🤖 ML Models":
        st.title("🤖 Machine Learning Models")
        st.markdown("### Train models and explore required skills for job streams")
        
        # ML Models Disclaimer
        st.info("""
        🤖 **Model Training Notice**: These machine learning models are trained on sample data for educational purposes. 
        Predictions and skill requirements are based on fictional job data and should not be used for real-world predictions.
        """)

        ml_model = st.session_state.ml_model

        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Model Training")
            if st.button("🚀 Train All Models", type="primary"):
                with st.spinner("Training models... This may take a moment."):
                    try:
                        results = ml_model.run_complete_ml_pipeline()
                        st.session_state.models_trained = True
                        st.success("✅ Models trained successfully!")
                        st.metric("Stream Predictor Accuracy", f"{results.get('stream_accuracy', 0):.2%}")
                        if results.get('demand_mse') is not None:
                            st.metric("Demand Forecaster MSE", f"{results.get('demand_mse', 0):.2f}")
                    except Exception as e:
                        st.error(f"❌ Training failed: {str(e)}")
            
            if st.session_state.models_trained:
                st.info("Models are trained and ready.")
            else:
                st.warning("Models are not trained yet.")

        with col2:
            st.subheader("🔍 Explore Stream Skills")
            
            if ml_model.df is not None and not ml_model.df.empty:
                all_streams = sorted(ml_model.df['Stream'].dropna().unique())
                
                selected_stream = st.selectbox("Select a Stream to see its required skills:", all_streams)

                if selected_stream:
                    # --- FINAL COMPREHENSIVE SKILL MAP ---
                    STREAM_SKILL_MAP = {
                        "Data Science & Analytics": ["python", "sql", "r", "tableau", "power bi", "excel", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "statistics", "machine learning", "warehousing", "etl", "spark", "hadoop", "sas", "matplotlib", "seaborn"],
                        "Artificial Intelligence & Machine Learning": ["python", "tensorflow", "pytorch", "scikit-learn", "nlp", "computer vision", "deep learning", "keras", "pandas", "numpy", "sql", "c++", "opencv"],
                        "Business Analysis": ["sql", "excel", "tableau", "power bi", "requirements gathering", "agile", "jira", "visio", "business process modeling", "srs"],
                        "Database Administration": ["sql", "mysql", "postgresql", "oracle", "database management", "performance tuning", "backup", "recovery", "nosql", "mongodb", "sql server"],
                        "Software Engineering": ["python", "java", "c++", "c#", "javascript", "go", "rust", "sql", "nosql", "docker", "kubernetes", "aws", "azure", "gcp", "git", "react", "angular", "vue", "node.js", "linux", "microservices", "api", "spring", "django", "flask"],
                        "Web Development": ["html", "css", "javascript", "react", "angular", "vue", "node.js", "php", "sql", "mongodb", "rest api", "bootstrap", "sass", "jquery", "typescript"],
                        "Mobile App Development": ["swift", "kotlin", "java", "react native", "flutter", "ios", "android", "api", "xcode", "android studio", "dart"],
                        "Cloud & DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible", "ci/cd", "jenkins", "linux", "python", "bash", "sql", "networking", "prometheus", "grafana"],
                        "Cyber Security": ["network security", "penetration testing", "siem", "cryptography", "firewall", "linux", "python", "wireshark", "iam", "cissp", "nessus", "nmap"],
                        "IT Infrastructure": ["active directory", "office 365", "networking", "hardware", "troubleshooting", "help desk", "linux", "windows server", "servicenow"],
                        "Quality Assurance": ["selenium", "junit", "testng", "automation", "jira", "bug tracking", "manual testing", "cypress", "postman", "loadrunner"],
                        "Data Engineering": ["python", "spark", "kafka", "airflow", "sql", "etl", "data warehousing", "big data", "hadoop", "scala", "databricks"],
                        "Network Engineering": ["cisco", "networking", "routing", "switching", "firewall", "network security", "tcp/ip", "bgp", "ospf", "vlans"],
                        "Product Management": ["agile", "scrum", "jira", "roadmap", "user research", "product strategy", "sql", "analytics", "market analysis", "prototyping"],
                        "Project Management": ["agile", "pmp", "scrum", "project planning", "budget management", "jira", "risk management", "ms project", "stakeholder management"],
                        "Finance": ["excel", "financial modeling", "accounting", "quickbooks", "sap", "valuation", "forecasting", "financial analysis"],
                        "Human Resources": ["recruiting", "onboarding", "employee relations", "hris", "performance management", "talent acquisition", "workday"],
                        "Sales": ["crm", "salesforce", "lead generation", "negotiation", "b2b", "b2c", "account management", "hubspot"],
                        "Marketing": ["seo", "sem", "content marketing", "social media", "google analytics", "email marketing", "hubspot", "salesforce", "google ads"],
                        "Design & UI/UX": ["figma", "sketch", "adobe xd", "user research", "wireframing", "prototyping", "ui", "ux", "css", "html", "photoshop", "illustrator", "invision"]
                    }

                    stream_df = ml_model.df[ml_model.df['Stream'] == selected_stream]
                    
                    # --- FINAL, HYBRID SKILL LOGIC ---
                    all_skills_in_stream = stream_df['Skills'].str.split(';').explode().str.strip().str.lower().dropna()
                    relevant_master_list = STREAM_SKILL_MAP.get(selected_stream, [])
                    
                    # 1. Find top skills that are ACTUALLY in the data AND in our master list.
                    valid_skills_from_data = all_skills_in_stream[all_skills_in_stream.isin(relevant_master_list)]
                    skill_counts = Counter(valid_skills_from_data)
                    top_skills_found = [skill for skill, count in skill_counts.most_common(10)]

                    # 2. If we found fewer than 10 skills, supplement the list with other expected skills.
                    top_skills_final = top_skills_found[:]
                    if len(top_skills_final) < 10:
                        supplemental_skills = [skill for skill in relevant_master_list if skill not in top_skills_final]
                        needed = 10 - len(top_skills_final)
                        top_skills_final.extend(supplemental_skills[:needed])
                    
                    # 3. If the stream wasn't in our map at all, fall back to a simple raw count.
                    if not relevant_master_list:
                        raw_counts = Counter(all_skills_in_stream)
                        top_skills_final = [skill for skill, count in raw_counts.most_common(10)]

                    st.info(f"**Top 10 skills for {selected_stream}:**")
                    st.markdown(f"`{', '.join(top_skills_final)}`")
                    
                    # Add a helpful note if the list was supplemented
                    if len(top_skills_found) < 10 and relevant_master_list:
                        st.caption(f"Note: Only {len(top_skills_found)} skills were found in the data file. The list was supplemented with other common skills for this role.")

                    st.markdown("---")
                    
                    user_skills_input = st.text_area("Paste your skills here (comma-separated) to compare:", height=100)
                    
                    if st.button("📊 Compare My Skills"):
                        if user_skills_input:
                            user_skills = set([s.strip().lower() for s in user_skills_input.split(',') if s])
                            required_skills = set(top_skills_final)
                            
                            matching_skills = user_skills.intersection(required_skills)
                            missing_skills = required_skills.difference(user_skills)
                            
                            match_percentage = (len(matching_skills) / len(required_skills)) * 100 if required_skills else 0
                            
                            st.metric("Your Skill Match vs. Top 10", f"{match_percentage:.1f}%")
                            
                            if matching_skills:
                                st.success(f"**Matching Skills:** {', '.join(matching_skills)}")
                            if missing_skills:
                                st.warning(f"**Missing Skills to Consider:** {', '.join(missing_skills)}")
                            if not missing_skills and user_skills:
                                st.balloons()
                                st.success("Excellent! You have all the top 10 skills for this stream.")
                        else:
                            st.error("Please enter your skills to compare.")
            else:
                st.warning("Data not loaded. Please ensure the data pipeline has been run.")

    elif main_option == "⚙️ Data Pipeline":
        st.title("⚙️ Data Pipeline Management")
        st.markdown("### Manage data ingestion and processing")
        
        # Data Pipeline Disclaimer
        st.info("""
        📊 **Data Information**: The data processed by this pipeline consists of sample job postings 
        created for demonstration purposes. All company names, job descriptions, and market data are fictional.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Run Data Pipeline", type="primary"):
                with st.spinner("Processing data..."):
                    try:
                        run_pipeline()
                        st.success("✅ Data pipeline completed successfully!")
                    except Exception as e:
                        st.error(f"❌ Pipeline failed: {str(e)}")
        
        with col2:
            if st.button("📊 Check Data Quality"):
                try:
                    import pandas as pd
                    from job_analysis.config import PROCESSED_DATA_PATH
                    
                    df = pd.read_csv(PROCESSED_DATA_PATH)
                    
                    st.metric("Total Records", len(df))
                    st.metric("Columns", len(df.columns))
                    st.metric("Missing Values", df.isnull().sum().sum())
                    
                    st.dataframe(df.head())
                    
                except Exception as e:
                    st.error(f"Error loading data: {str(e)}")

if __name__ == "__main__":
    main()

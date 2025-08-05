# src/resume_interface.py - Clean resume matching interface

import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import logging
import re

# Set up logging
logger = logging.getLogger(__name__)

class ResumeMatchingInterface:
    """
    Clean and robust resume matching interface.
    """
    
    def __init__(self):
        """Initialize the resume matcher."""
        self.df = None
        self.skill_mapping = self._get_skill_mapping()
        self.load_data()
    
    def load_data(self):
        """Load processed data."""
        try:
            from job_analysis.config import PROCESSED_DATA_PATH
            import os
            
            if os.path.exists(PROCESSED_DATA_PATH):
                self.df = pd.read_csv(PROCESSED_DATA_PATH)
                logger.info(f"Loaded {len(self.df)} records for resume matching")
            else:
                logger.warning("Processed data file not found")
                self.df = None
        except Exception as e:
            logger.error(f"Failed to load data: {str(e)}")
            self.df = None
    
    def _get_skill_mapping(self):
        """Get comprehensive skill mapping for different job streams."""
        return {
            "Data Science & Analytics": [
                "python", "sql", "r", "tableau", "power bi", "excel", "pandas", "numpy", 
                "scikit-learn", "tensorflow", "pytorch", "statistics", "machine learning", 
                "data warehousing", "etl", "spark", "hadoop", "matplotlib", "seaborn", "plotly"
            ],
            "Artificial Intelligence & Machine Learning": [
                "python", "tensorflow", "pytorch", "scikit-learn", "nlp", "computer vision", 
                "deep learning", "keras", "pandas", "numpy", "sql", "opencv", "transformers", 
                "neural networks", "reinforcement learning"
            ],
            "Software Engineering": [
                "python", "java", "c++", "c#", "javascript", "go", "rust", "sql", "nosql", 
                "docker", "kubernetes", "aws", "azure", "git", "microservices", "api", 
                "spring", "django", "flask", "rest api", "graphql"
            ],
            "Web Development": [
                "html", "css", "javascript", "react", "angular", "vue", "node.js", "php", 
                "sql", "mongodb", "rest api", "bootstrap", "sass", "jquery", "typescript", 
                "webpack", "express", "laravel"
            ],
            "Mobile App Development": [
                "swift", "kotlin", "java", "react native", "flutter", "ios", "android", 
                "api", "xcode", "android studio", "dart", "objective-c", "xamarin"
            ],
            "Cloud & DevOps": [
                "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible", 
                "ci/cd", "jenkins", "linux", "python", "bash", "networking", "prometheus", 
                "grafana", "helm", "serverless"
            ],
            "Cyber Security": [
                "network security", "penetration testing", "siem", "cryptography", "firewall", 
                "linux", "python", "wireshark", "iam", "cissp", "nessus", "nmap", "vulnerability assessment"
            ],
            "Business Analysis": [
                "sql", "excel", "tableau", "power bi", "requirements gathering", "agile", 
                "jira", "visio", "business process modeling", "stakeholder management", "user stories"
            ],
            "Database Administration": [
                "sql", "mysql", "postgresql", "oracle", "database management", "performance tuning", 
                "backup", "recovery", "nosql", "mongodb", "sql server", "database design"
            ],
            "Product Management": [
                "agile", "scrum", "jira", "roadmap", "user research", "product strategy", 
                "sql", "analytics", "market analysis", "prototyping", "stakeholder management"
            ],
            "Design & UI/UX": [
                "figma", "sketch", "adobe xd", "user research", "wireframing", "prototyping", 
                "ui", "ux", "css", "html", "photoshop", "illustrator", "user testing"
            ],
            "Quality Assurance": [
                "selenium", "junit", "testng", "automation", "jira", "bug tracking", 
                "manual testing", "api testing", "performance testing", "test planning"
            ],
            "Data Engineering": [
                "python", "spark", "kafka", "airflow", "sql", "etl", "data warehousing", 
                "big data", "hadoop", "redshift", "snowflake", "databricks"
            ],
            "IT Infrastructure": [
                "linux", "windows server", "networking", "active directory", "virtualization", 
                "monitoring", "vmware", "hyper-v", "powershell", "bash"
            ],
            "Network Engineering": [
                "cisco", "networking", "routing", "switching", "firewall", "network security", 
                "tcp/ip", "vpn", "load balancing", "network monitoring"
            ]
        }
    
    def run_interface(self):
        """Main resume matching interface."""
        st.title("🎯 AI-Powered Resume Matcher")
        st.markdown("### Match your skills with job requirements and get personalized recommendations")
        
        # Resume Matcher Disclaimer
        st.info("""
        🎯 **Demo Notice**: This resume matcher analyzes skills against sample job data for demonstration purposes. 
        Job recommendations and skill suggestions are based on fictional job postings and should not be used for actual career decisions.
        """)
        
        if self.df is None or self.df.empty:
            st.error("❌ No job data available for matching.")
            st.info("💡 Please run the Data Pipeline to generate or process data first.")
            return
        
        # Interface sections
        self.show_stream_selection()
        st.markdown("---")
        self.show_skill_input_section()
        st.markdown("---")
        self.show_job_recommendations()
    
    def show_stream_selection(self):
        """Display stream selection and overview."""
        st.subheader("🎯 Select Your Target Job Stream")
        
        if self.df is None or 'Stream' not in self.df.columns:
            st.error("Stream data not available in dataset")
            return
        
        streams = sorted(self.df['Stream'].unique())
        selected_stream = st.selectbox("Choose a job stream:", streams)
        
        if selected_stream:
            # Store in session state for other methods
            st.session_state.selected_stream = selected_stream
            
            # Stream overview
            stream_df = self.df[self.df['Stream'] == selected_stream]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Available Jobs", len(stream_df))
            with col2:
                unique_companies = stream_df['Company'].nunique() if 'Company' in stream_df.columns else 0
                st.metric("Companies Hiring", unique_companies)
            with col3:
                unique_locations = stream_df['Location'].nunique() if 'Location' in stream_df.columns else 0
                st.metric("Locations", unique_locations)
            
            # Expected skills for the stream
            expected_skills = self.skill_mapping.get(selected_stream, [])
            if expected_skills:
                st.markdown(f"#### 🛠️ Key Skills for {selected_stream}:")
                self.display_skills_as_badges(expected_skills[:12])  # Show top 12 skills
            
            # Analyze actual skills from job data
            self.show_actual_skills_from_jobs(stream_df)
    
    def show_actual_skills_from_jobs(self, stream_df):
        """Show skills extracted from actual job postings."""
        if 'Skills' not in stream_df.columns:
            return
        
        try:
            all_skills = stream_df['Skills'].str.split(';').explode().str.strip().str.lower()
            skill_counts = Counter(all_skills.dropna())
            top_actual_skills = [skill for skill, count in skill_counts.most_common(10)]
            
            if top_actual_skills:
                st.markdown("#### 📊 Most Frequent Skills in Job Postings:")
                self.display_skills_as_badges(top_actual_skills, color="#28a745")
        except Exception as e:
            logger.error(f"Error analyzing actual skills: {str(e)}")
    
    def display_skills_as_badges(self, skills, color="#1f77b4"):
        """Display skills as colored badges."""
        skills_html = ""
        for skill in skills:
            skills_html += f'<span style="background-color: {color}; color: white; padding: 3px 8px; margin: 2px; border-radius: 10px; font-size: 12px;">{skill}</span> '
        st.markdown(skills_html, unsafe_allow_html=True)
    
    def show_skill_input_section(self):
        """Display skill input and analysis section."""
        st.subheader("📝 Analyze Your Skills")
        
        if 'selected_stream' not in st.session_state:
            st.warning("Please select a job stream first.")
            return
        
        selected_stream = st.session_state.selected_stream
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Skill input methods
            input_method = st.radio(
                "Choose input method:",
                ["Text Input", "Resume Upload"],
                horizontal=True
            )
            
            if input_method == "Text Input":
                user_skills_input = st.text_area(
                    "Enter your skills (comma-separated):",
                    height=120,
                    placeholder="python, sql, machine learning, pandas, statistics, tableau...",
                    help="List your technical and soft skills separated by commas"
                )
                
                if st.button("🔍 Analyze My Skills", type="primary"):
                    if user_skills_input:
                        self.analyze_skills(user_skills_input, selected_stream)
                    else:
                        st.error("Please enter your skills to analyze.")
            
            else:  # Resume Upload
                uploaded_file = st.file_uploader(
                    "Upload your resume",
                    type=['pdf', 'docx', 'txt'],
                    help="Upload your resume in PDF, DOCX, or TXT format"
                )
                
                if uploaded_file is not None:
                    if st.button("📄 Extract Skills from Resume", type="primary"):
                        extracted_skills = self.extract_skills_from_resume(uploaded_file)
                        if extracted_skills:
                            self.analyze_skills(extracted_skills, selected_stream)
                        else:
                            st.error("Could not extract skills from the resume.")
        
        with col2:
            st.markdown("#### 💡 Tips for Better Matching")
            st.info("""
            **For Text Input:**
            • Use lowercase for better matching
            • Be specific (e.g., 'python' vs 'programming')
            • Include both technical and soft skills
            • Separate skills with commas
            
            **For Resume Upload:**
            • Use clear, well-formatted documents
            • Include a dedicated skills section
            • List specific technologies and tools
            """)
    
    def extract_skills_from_resume(self, uploaded_file):
        """Extract skills from uploaded resume."""
        try:
            # Read file content based on type
            content = ""
            if uploaded_file.type == "text/plain":
                content = str(uploaded_file.read(), "utf-8")
            elif uploaded_file.type == "application/pdf":
                # For PDF extraction, we'll use a simple approach
                # In production, you'd use PyPDF2 or similar
                st.warning("PDF extraction requires additional libraries. Please use text input for now.")
                return None
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                # For DOCX extraction
                st.warning("DOCX extraction requires additional libraries. Please use text input for now.")
                return None
            
            if content:
                # Simple skill extraction using regex and known skills
                all_possible_skills = set()
                for skills_list in self.skill_mapping.values():
                    all_possible_skills.update(skills_list)
                
                found_skills = []
                content_lower = content.lower()
                
                for skill in all_possible_skills:
                    if skill.lower() in content_lower:
                        found_skills.append(skill)
                
                if found_skills:
                    skills_text = ", ".join(found_skills)
                    st.success(f"Extracted {len(found_skills)} skills from resume")
                    st.text_area("Extracted skills:", skills_text, height=100)
                    return skills_text
                else:
                    st.warning("No recognizable skills found in the resume.")
                    return None
            
        except Exception as e:
            st.error(f"Error processing resume: {str(e)}")
            return None
    
    def analyze_skills(self, user_skills_input, selected_stream):
        """Analyze user skills against job requirements."""
        # Parse user skills
        user_skills = set([s.strip().lower() for s in user_skills_input.split(',') if s.strip()])
        
        # Get required skills for the stream
        required_skills_set = set(self.skill_mapping.get(selected_stream, []))
        
        # Calculate matches
        matching_skills = user_skills.intersection(required_skills_set)
        missing_skills = required_skills_set.difference(user_skills)
        extra_skills = user_skills.difference(required_skills_set)
        
        match_percentage = (len(matching_skills) / len(required_skills_set)) * 100 if required_skills_set else 0
        
        # Store analysis results in session state
        st.session_state.skill_analysis = {
            'user_skills': user_skills,
            'matching_skills': matching_skills,
            'missing_skills': missing_skills,
            'extra_skills': extra_skills,
            'match_percentage': match_percentage
        }
        
        # Display results
        self.display_skill_analysis_results()
    
    def display_skill_analysis_results(self):
        """Display the results of skill analysis."""
        if 'skill_analysis' not in st.session_state:
            return
        
        analysis = st.session_state.skill_analysis
        
        st.markdown("### 📊 Skill Analysis Results")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Skill Match Score", f"{analysis['match_percentage']:.1f}%")
        with col2:
            st.metric("Skills Matched", f"{len(analysis['matching_skills'])}/{len(analysis['matching_skills']) + len(analysis['missing_skills'])}")
        with col3:
            st.metric("Additional Skills", len(analysis['extra_skills']))
        
        # Detailed breakdown
        if analysis['matching_skills']:
            st.success(f"**✅ Matching Skills ({len(analysis['matching_skills'])}):**")
            self.display_skills_as_badges(list(analysis['matching_skills']), "#28a745")
        
        if analysis['missing_skills']:
            st.warning(f"**⚠️ Skills to Develop ({len(analysis['missing_skills'])}):**")
            self.display_skills_as_badges(list(analysis['missing_skills']), "#ffc107")
        
        if analysis['extra_skills']:
            st.info(f"**💡 Additional Skills ({len(analysis['extra_skills'])}):**")
            self.display_skills_as_badges(list(analysis['extra_skills']), "#17a2b8")
        
        # Recommendations
        self.show_recommendations(analysis['match_percentage'], analysis['missing_skills'])
    
    def show_recommendations(self, match_percentage, missing_skills):
        """Show personalized recommendations based on analysis."""
        st.markdown("### 🎯 Personalized Recommendations")
        
        if match_percentage >= 80:
            st.balloons()
            st.success("🎉 Excellent match! You have most of the required skills for this field.")
            st.markdown("""
            **Next Steps:**
            - Apply for senior positions in your target companies
            - Consider specializing in emerging technologies
            - Look into leadership or mentoring roles
            - Contribute to open-source projects to showcase your skills
            """)
        elif match_percentage >= 60:
            st.success("👍 Good match! Focus on developing the missing skills to improve your profile.")
            if missing_skills:
                priority_skills = list(missing_skills)[:3]
                st.markdown(f"**Priority Skills to Learn:** {', '.join(priority_skills)}")
                st.markdown("""
                **Recommended Actions:**
                - Take online courses for the missing skills
                - Work on projects that incorporate these skills
                - Consider certifications in key areas
                """)
        else:
            st.info("📚 Focus on building the core skills for this field.")
            if missing_skills:
                core_skills = list(missing_skills)[:5]
                st.markdown(f"**Core Skills to Focus On:** {', '.join(core_skills)}")
                st.markdown("""
                **Learning Path:**
                - Start with foundational courses
                - Build practical projects
                - Join communities and forums
                - Consider bootcamps or formal education
                """)
    
    def show_job_recommendations(self):
        """Show recommended jobs based on skill analysis."""
        if 'skill_analysis' not in st.session_state or 'selected_stream' not in st.session_state:
            return
        
        analysis = st.session_state.skill_analysis
        selected_stream = st.session_state.selected_stream
        
        if analysis['match_percentage'] < 40:
            return  # Don't show job recommendations for very low matches
        
        st.subheader("💼 Recommended Job Opportunities")
        
        # Filter jobs for the selected stream
        if self.df is not None:
            stream_df = self.df[self.df['Stream'] == selected_stream]
        else:
            st.error("Job data is not available.")
            return
        
        # For now, show top jobs (could be enhanced with actual matching logic)
        recommended_jobs = stream_df.head(5)
        
        for idx, job in recommended_jobs.iterrows():
            with st.expander(f"🎯 {job['Job Title']} at {job['Company']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**📍 Location:** {job['Location']}")
                    if 'Salary_Range' in job:
                        st.markdown(f"**💰 Salary:** {job['Salary_Range']}")
                    if 'Experience_Level' in job:
                        st.markdown(f"**📊 Experience:** {job['Experience_Level']}")
                
                with col2:
                    if 'Skills' in job:
                        job_skills = set([s.strip().lower() for s in str(job['Skills']).split(';')])
                        user_skills = analysis['user_skills']
                        job_match = len(user_skills.intersection(job_skills)) / len(job_skills) if job_skills else 0
                        
                        st.metric("Skill Match", f"{job_match:.1%}")
                        
                        # Show matching skills for this specific job
                        matching_job_skills = user_skills.intersection(job_skills)
                        if matching_job_skills:
                            st.markdown("**Your matching skills:**")
                            self.display_skills_as_badges(list(matching_job_skills)[:5], "#28a745")
                
                # Full skill requirements
                if 'Skills' in job:
                    st.markdown("**Required Skills:**")
                    job_skills_list = [s.strip() for s in str(job['Skills']).split(';')]
                    self.display_skills_as_badges(job_skills_list, "#6c757d")
                
                # Application advice
                if analysis['match_percentage'] >= 70:
                    st.success("✅ Strong candidate - consider applying!")
                elif analysis['match_percentage'] >= 50:
                    st.info("💡 Good fit - highlight relevant experience")
                else:
                    st.warning("⚠️ May need skill development first")
        
        # Additional job search tips
        with st.expander("💡 Job Search Tips"):
            st.markdown("""
            **Before Applying:**
            - Tailor your resume to highlight matching skills
            - Research the company and role thoroughly
            - Prepare examples of how you've used relevant technologies
            - Practice explaining complex technical concepts simply
            
            **During Interviews:**
            - Be honest about your skill level
            - Show enthusiasm for learning missing skills
            - Highlight transferable skills and experience
            - Ask thoughtful questions about the role and team
            """)
    
    def generate_learning_plan(self, missing_skills):
        """Generate a personalized learning plan."""
        if not missing_skills:
            return
        
        st.markdown("### 📚 Personalized Learning Plan")
        
        # Categorize skills
        skill_categories = {
            'Programming Languages': ['python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby'],
            'Data & Analytics': ['sql', 'tableau', 'power bi', 'excel', 'pandas', 'numpy', 'matplotlib', 'seaborn'],
            'Machine Learning': ['scikit-learn', 'tensorflow', 'pytorch', 'keras', 'machine learning', 'deep learning'],
            'Cloud & DevOps': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ci/cd'],
            'Web Development': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express'],
            'Databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'oracle'],
        }
        
        categorized_missing = {}
        for category, skills in skill_categories.items():
            category_missing = [skill for skill in missing_skills if skill in skills]
            if category_missing:
                categorized_missing[category] = category_missing
        
        for category, skills in categorized_missing.items():
            with st.expander(f"📖 {category} Learning Path"):
                for skill in skills:
                    st.markdown(f"**{skill.title()}:**")
                    st.markdown(f"• Start with online tutorials and documentation")
                    st.markdown(f"• Build practice projects")
                    st.markdown(f"• Join communities and forums")
                    st.markdown("---")

# src/job_scraper.py

import requests
import time
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import json
import logging
import sqlite3
from typing import Dict, List, Optional
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import schedule
from dataclasses import dataclass
import random

from job_analysis.config import LOG_FILE

@dataclass
class JobPosting:
    """Data class for job postings"""
    title: str
    company: str
    location: str
    description: str
    skills: str
    salary: Optional[str]
    date_posted: str
    url: str
    source: str
    job_type: str
    experience_level: str
    stream: str

class JobScrapingEngine:
    """
    Professional job scraping engine with multiple sources
    """
    
    def __init__(self, database_path='data/jobs.db'):
        self.database_path = database_path
        self.setup_database()
        self.setup_selenium()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
    def setup_database(self):
        """Setup SQLite database for job storage"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_postings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT NOT NULL,
                    description TEXT,
                    skills TEXT,
                    salary TEXT,
                    date_posted TEXT,
                    url TEXT UNIQUE,
                    source TEXT,
                    job_type TEXT,
                    experience_level TEXT,
                    stream TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_company ON job_postings(company)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_location ON job_postings(location)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_stream ON job_postings(stream)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_date_posted ON job_postings(date_posted)')
            
            conn.commit()
            conn.close()
            
            print("✅ Database setup completed")
            
        except Exception as e:
            logging.error(f"Database setup error: {str(e)}")
            raise
    
    def setup_selenium(self):
        """Setup Selenium WebDriver"""
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
    
    def get_random_headers(self):
        """Get random headers for requests"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def classify_job_stream(self, title: str, description: str) -> str:
        """AI-powered job stream classification"""
        title_lower = title.lower()
        desc_lower = description.lower()
        
        # Define classification rules
        stream_keywords = {
            'Software Engineering': ['software', 'developer', 'programming', 'backend', 'frontend', 'full stack'],
            'Data Science': ['data scientist', 'machine learning', 'ai', 'analytics', 'big data', 'python'],
            'DevOps': ['devops', 'cloud', 'aws', 'azure', 'docker', 'kubernetes', 'infrastructure'],
            'Product Management': ['product manager', 'pm', 'product owner', 'strategy', 'roadmap'],
            'Design': ['ui/ux', 'designer', 'user experience', 'user interface', 'figma'],
            'Marketing': ['marketing', 'digital marketing', 'seo', 'content', 'social media'],
            'Sales': ['sales', 'business development', 'account manager', 'revenue'],
            'HR': ['human resources', 'hr', 'recruiter', 'talent acquisition', 'people'],
            'Finance': ['finance', 'accounting', 'financial analyst', 'controller', 'cfo'],
            'Operations': ['operations', 'supply chain', 'logistics', 'process improvement']
        }
        
        # Score each stream
        stream_scores = {}
        for stream, keywords in stream_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in title_lower:
                    score += 3  # Title matches are weighted higher
                if keyword in desc_lower:
                    score += 1
            stream_scores[stream] = score
        
        # Return highest scoring stream
        if stream_scores:
            return max(stream_scores, key=lambda k: stream_scores[k])
        return 'Other'
    
    def scrape_indeed_jobs(self, search_terms: List[str], location: str = "United States", max_pages: int = 5) -> List[JobPosting]:
        """Scrape jobs from Indeed"""
        jobs = []
        
        try:
            for search_term in search_terms:
                print(f"🔍 Scraping Indeed for: {search_term}")
                
                for page in range(max_pages):
                    url = f"https://www.indeed.com/jobs?q={search_term}&l={location}&start={page * 10}"
                    
                    driver = webdriver.Chrome(options=self.chrome_options)
                    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    
                    try:
                        driver.get(url)
                        time.sleep(random.uniform(2, 5))  # Random delay
                        
                        # Wait for job cards to load
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-jk]"))
                        )
                        
                        job_cards = driver.find_elements(By.CSS_SELECTOR, "[data-jk]")
                        
                        for card in job_cards:
                            try:
                                # Extract job information
                                title_elem = card.find_element(By.CSS_SELECTOR, "h2 a span")
                                company_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='company-name']")
                                location_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='job-location']")
                                
                                title = title_elem.text.strip()
                                company = company_elem.text.strip()
                                location = location_elem.text.strip()
                                
                                # Get job URL
                                job_url = card.find_element(By.CSS_SELECTOR, "h2 a").get_attribute('href')
                                
                                # Extract salary if available
                                salary = ""
                                try:
                                    salary_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='salary-snippet']")
                                    salary = salary_elem.text.strip()
                                except:
                                    pass
                                
                                # Get job description (simplified)
                                description = ""
                                try:
                                    desc_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='job-snippet']")
                                    description = desc_elem.text.strip()
                                except:
                                    pass
                                
                                # Extract skills from description
                                skills = self.extract_skills_from_text(f"{title} {description}")
                                
                                # Classify job stream
                                stream = self.classify_job_stream(title, description)
                                
                                job = JobPosting(
                                    title=title,
                                    company=company,
                                    location=location,
                                    description=description,
                                    skills=', '.join(skills),
                                    salary=salary,
                                    date_posted=datetime.now().strftime('%Y-%m-%d'),
                                    url=job_url or '',
                                    source='Indeed',
                                    job_type='Full-time',
                                    experience_level='Mid-level',
                                    stream=stream
                                )
                                
                                jobs.append(job)
                                
                            except Exception as e:
                                logging.error(f"Error parsing job card: {str(e)}")
                                continue
                    
                    except Exception as e:
                        logging.error(f"Error scraping Indeed page: {str(e)}")
                    
                    finally:
                        driver.quit()
                    
                    # Random delay between pages
                    time.sleep(random.uniform(3, 7))
                
                print(f"✅ Scraped {len(jobs)} jobs from Indeed for {search_term}")
                
        except Exception as e:
            logging.error(f"Error in Indeed scraping: {str(e)}")
        
        return jobs
    
    def scrape_glassdoor_jobs(self, search_terms: List[str], location: str = "United States", max_pages: int = 3) -> List[JobPosting]:
        """Scrape jobs from Glassdoor"""
        jobs = []
        
        try:
            for search_term in search_terms:
                print(f"🔍 Scraping Glassdoor for: {search_term}")
                
                for page in range(max_pages):
                    url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={search_term}&locT=N&locId=1&p={page + 1}"
                    
                    driver = webdriver.Chrome(options=self.chrome_options)
                    
                    try:
                        driver.get(url)
                        time.sleep(random.uniform(3, 6))
                        
                        # Handle potential popups
                        try:
                            close_button = driver.find_element(By.CSS_SELECTOR, "[data-test='modal-close']")
                            close_button.click()
                        except:
                            pass
                        
                        # Wait for job listings
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='job-listing']"))
                        )
                        
                        job_cards = driver.find_elements(By.CSS_SELECTOR, "[data-test='job-listing']")
                        
                        for card in job_cards:
                            try:
                                title_elem = card.find_element(By.CSS_SELECTOR, "[data-test='job-title']")
                                company_elem = card.find_element(By.CSS_SELECTOR, "[data-test='employer-name']")
                                location_elem = card.find_element(By.CSS_SELECTOR, "[data-test='job-location']")
                                
                                title = title_elem.text.strip()
                                company = company_elem.text.strip()
                                location = location_elem.text.strip()
                                
                                # Get job URL
                                job_url = title_elem.get_attribute('href')
                                
                                # Extract salary if available
                                salary = ""
                                try:
                                    salary_elem = card.find_element(By.CSS_SELECTOR, "[data-test='salary-estimate']")
                                    salary = salary_elem.text.strip()
                                except:
                                    pass
                                
                                # Get job description
                                description = ""
                                try:
                                    desc_elem = card.find_element(By.CSS_SELECTOR, "[data-test='job-description']")
                                    description = desc_elem.text.strip()
                                except:
                                    pass
                                
                                # Extract skills
                                skills = self.extract_skills_from_text(f"{title} {description}")
                                
                                # Classify stream
                                stream = self.classify_job_stream(title, description)
                                
                                job = JobPosting(
                                    title=title,
                                    company=company,
                                    location=location,
                                    description=description,
                                    skills=', '.join(skills),
                                    salary=salary,
                                    date_posted=datetime.now().strftime('%Y-%m-%d'),
                                    url=job_url or '',
                                    source='Glassdoor',
                                    job_type='Full-time',
                                    experience_level='Mid-level',
                                    stream=stream
                                )
                                
                                jobs.append(job)
                                
                            except Exception as e:
                                logging.error(f"Error parsing Glassdoor job card: {str(e)}")
                                continue
                    
                    except Exception as e:
                        logging.error(f"Error scraping Glassdoor page: {str(e)}")
                    
                    finally:
                        driver.quit()
                    
                    # Random delay
                    time.sleep(random.uniform(4, 8))
                
                print(f"✅ Scraped {len(jobs)} jobs from Glassdoor for {search_term}")
                
        except Exception as e:
            logging.error(f"Error in Glassdoor scraping: {str(e)}")
        
        return jobs
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from job text"""
        skills = []
        text_lower = text.lower()
        
        # Technical skills database
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'aws', 'azure', 'docker', 'kubernetes', 'terraform', 'ansible',
            'machine learning', 'ai', 'data science', 'pandas', 'numpy',
            'git', 'jenkins', 'jira', 'agile', 'scrum', 'devops',
            'html', 'css', 'bootstrap', 'sass', 'webpack', 'rest api',
            'microservices', 'spring', 'django', 'flask', 'express'
        ]
        
        for skill in skill_keywords:
            if skill in text_lower:
                skills.append(skill)
        
        return skills
    
    def save_jobs_to_database(self, jobs: List[JobPosting]):
        """Save scraped jobs to database"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            saved_count = 0
            
            for job in jobs:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO job_postings 
                        (title, company, location, description, skills, salary, 
                         date_posted, url, source, job_type, experience_level, stream)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        job.title, job.company, job.location, job.description,
                        job.skills, job.salary, job.date_posted, job.url,
                        job.source, job.job_type, job.experience_level, job.stream
                    ))
                    
                    if cursor.rowcount > 0:
                        saved_count += 1
                        
                except Exception as e:
                    logging.error(f"Error saving job to database: {str(e)}")
                    continue
            
            conn.commit()
            conn.close()
            
            print(f"✅ Saved {saved_count} new jobs to database")
            return saved_count
            
        except Exception as e:
            logging.error(f"Database save error: {str(e)}")
            return 0
    
    def get_jobs_from_database(self, limit: int = 1000) -> pd.DataFrame:
        """Get jobs from database as DataFrame"""
        try:
            conn = sqlite3.connect(self.database_path)
            query = '''
                SELECT title, company, location, description, skills, salary,
                       date_posted, url, source, job_type, experience_level, stream,
                       scraped_at
                FROM job_postings
                ORDER BY scraped_at DESC
                LIMIT ?
            '''
            
            df = pd.read_sql_query(query, conn, params=(limit,))
            conn.close()
            
            return df
            
        except Exception as e:
            logging.error(f"Error retrieving jobs from database: {str(e)}")
            return pd.DataFrame()
    
    def run_daily_scraping(self):
        """Run daily scraping job"""
        print("🚀 Starting daily job scraping...")
        
        # Define search terms
        search_terms = [
            'software engineer', 'data scientist', 'product manager',
            'devops engineer', 'full stack developer', 'machine learning',
            'frontend developer', 'backend developer', 'ui ux designer'
        ]
        
        all_jobs = []
        
        # Scrape from Indeed
        indeed_jobs = self.scrape_indeed_jobs(search_terms, max_pages=3)
        all_jobs.extend(indeed_jobs)
        
        # Scrape from Glassdoor
        glassdoor_jobs = self.scrape_glassdoor_jobs(search_terms, max_pages=2)
        all_jobs.extend(glassdoor_jobs)
        
        # Save to database
        saved_count = self.save_jobs_to_database(all_jobs)
        
        print(f"🎉 Daily scraping completed! Scraped {len(all_jobs)} jobs, saved {saved_count} new jobs")
        
        return len(all_jobs), saved_count
    
    def schedule_scraping(self):
        """Schedule automatic scraping"""
        print("⏰ Setting up scheduled job scraping...")
        
        # Schedule daily scraping at 9 AM
        schedule.every().day.at("09:00").do(self.run_daily_scraping)
        
        # Schedule lighter scraping every 6 hours
        schedule.every(6).hours.do(lambda: self.run_daily_scraping())
        
        print("✅ Scheduling setup complete")
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

# Usage example
if __name__ == "__main__":
    scraper = JobScrapingEngine()
    
    # Run one-time scraping
    total_jobs, saved_jobs = scraper.run_daily_scraping()
    
    # Get scraped jobs as DataFrame
    df = scraper.get_jobs_from_database(limit=100)
    print(f"📊 Retrieved {len(df)} jobs from database")
    print(df.head())

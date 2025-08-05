# src/realtime_processor.py

import pandas as pd
import sqlite3
import asyncio
import websockets
import json
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import threading
import time
import schedule
from dataclasses import dataclass, asdict
import numpy as np
from collections import defaultdict, deque
import streamlit as st
from concurrent.futures import ThreadPoolExecutor

from src.job_scraper import JobScrapingEngine
from src.eda_module import JobAnalyticsEDA
from job_analysis.config import LOG_FILE

class RealTimeJobProcessor:
    """
    Real-time job data processing and analytics engine
    """
    
    def __init__(self, database_path='data/jobs.db'):
        self.database_path = database_path
        self.scraper = JobScrapingEngine(database_path)
        self.analytics_cache = {}
        self.subscribers = set()
        self.running = False
        self.job_queue = deque(maxlen=1000)
        self.metrics = {
            'total_processed': 0,
            'processing_rate': 0,
            'last_update': datetime.now(),
            'errors': 0
        }
        
    def start_real_time_processing(self):
        """Start real-time processing"""
        self.running = True
        print("🚀 Starting real-time job processing...")
        
        # Start background threads
        threading.Thread(target=self._process_job_queue, daemon=True).start()
        threading.Thread(target=self._update_analytics, daemon=True).start()
        threading.Thread(target=self._cleanup_old_data, daemon=True).start()
        
        print("✅ Real-time processing started")
    
    def stop_real_time_processing(self):
        """Stop real-time processing"""
        self.running = False
        print("⏹️ Real-time processing stopped")
    
    def _process_job_queue(self):
        """Process incoming jobs from queue"""
        while self.running:
            try:
                if self.job_queue:
                    job = self.job_queue.popleft()
                    self._process_single_job(job)
                    self.metrics['total_processed'] += 1
                else:
                    time.sleep(1)  # Wait if queue is empty
                    
            except Exception as e:
                logging.error(f"Error processing job queue: {str(e)}")
                self.metrics['errors'] += 1
                time.sleep(1)
    
    def _process_single_job(self, job_data: dict):
        """Process a single job posting"""
        try:
            # Enhanced job analysis
            enhanced_job = self._enhance_job_data(job_data)
            
            # Update analytics cache
            self._update_analytics_cache(enhanced_job)
            
            # Notify subscribers
            self._notify_subscribers(enhanced_job)
            
        except Exception as e:
            logging.error(f"Error processing single job: {str(e)}")
    
    def _enhance_job_data(self, job_data: dict) -> dict:
        """Enhance job data with additional analytics"""
        enhanced = job_data.copy()
        
        # Add trend indicators
        enhanced['trend_score'] = self._calculate_trend_score(job_data)
        enhanced['popularity_score'] = self._calculate_popularity_score(job_data)
        enhanced['urgency_score'] = self._calculate_urgency_score(job_data)
        
        # Add market analysis
        enhanced['market_analysis'] = self._analyze_job_market_position(job_data)
        
        return enhanced
    
    def _calculate_trend_score(self, job_data: dict) -> float:
        """Calculate job trend score based on recent postings"""
        try:
            # Get recent jobs in same stream
            conn = sqlite3.connect(self.database_path)
            query = '''
                SELECT COUNT(*) as count
                FROM job_postings
                WHERE stream = ? AND date_posted >= date('now', '-7 days')
            '''
            
            result = conn.execute(query, (job_data.get('stream', ''),)).fetchone()
            conn.close()
            
            # Normalize trend score (0-100)
            count = result[0] if result else 0
            return min(100, count * 2)  # Scale factor
            
        except Exception as e:
            logging.error(f"Error calculating trend score: {str(e)}")
            return 0.0
    
    def _calculate_popularity_score(self, job_data: dict) -> float:
        """Calculate job popularity score"""
        try:
            # Factors: company size, location popularity, skill demand
            score = 0
            
            # Company popularity
            conn = sqlite3.connect(self.database_path)
            company_count = conn.execute(
                'SELECT COUNT(*) FROM job_postings WHERE company = ?',
                (job_data.get('company', ''),)
            ).fetchone()[0]
            
            # Location popularity
            location_count = conn.execute(
                'SELECT COUNT(*) FROM job_postings WHERE location = ?',
                (job_data.get('location', ''),)
            ).fetchone()[0]
            
            conn.close()
            
            # Calculate weighted score
            score = (company_count * 0.4) + (location_count * 0.3) + (len(job_data.get('skills', '').split(',')) * 0.3)
            
            return min(100, score)
            
        except Exception as e:
            logging.error(f"Error calculating popularity score: {str(e)}")
            return 0.0
    
    def _calculate_urgency_score(self, job_data: dict) -> float:
        """Calculate job urgency score"""
        try:
            # Based on keywords in title/description
            urgency_keywords = [
                'urgent', 'immediate', 'asap', 'now hiring',
                'start immediately', 'quick start', 'fast track'
            ]
            
            text = f"{job_data.get('title', '')} {job_data.get('description', '')}".lower()
            
            urgency_score = 0
            for keyword in urgency_keywords:
                if keyword in text:
                    urgency_score += 20
            
            return min(100, urgency_score)
            
        except Exception as e:
            logging.error(f"Error calculating urgency score: {str(e)}")
            return 0.0
    
    def _analyze_job_market_position(self, job_data: dict) -> dict:
        """Analyze job's position in the market"""
        try:
            analysis = {
                'stream_competition': 'Medium',
                'salary_range': 'Competitive',
                'location_demand': 'High',
                'skill_rarity': 'Common'
            }
            
            # Get stream statistics
            conn = sqlite3.connect(self.database_path)
            
            # Stream competition
            stream_count = conn.execute(
                'SELECT COUNT(*) FROM job_postings WHERE stream = ?',
                (job_data.get('stream', ''),)
            ).fetchone()[0]
            
            if stream_count > 100:
                analysis['stream_competition'] = 'High'
            elif stream_count < 20:
                analysis['stream_competition'] = 'Low'
            
            # Location demand
            location_count = conn.execute(
                'SELECT COUNT(*) FROM job_postings WHERE location = ?',
                (job_data.get('location', ''),)
            ).fetchone()[0]
            
            if location_count > 50:
                analysis['location_demand'] = 'High'
            elif location_count < 10:
                analysis['location_demand'] = 'Low'
            else:
                analysis['location_demand'] = 'Medium'
            
            conn.close()
            
            return analysis
            
        except Exception as e:
            logging.error(f"Error analyzing market position: {str(e)}")
            return {}
    
    def _update_analytics_cache(self, job_data: dict):
        """Update analytics cache with new job data"""
        try:
            now = datetime.now()
            cache_key = now.strftime('%Y-%m-%d-%H')  # Hourly cache
            
            if cache_key not in self.analytics_cache:
                self.analytics_cache[cache_key] = {
                    'total_jobs': 0,
                    'streams': defaultdict(int),
                    'locations': defaultdict(int),
                    'companies': defaultdict(int),
                    'skills': defaultdict(int),
                    'trends': []
                }
            
            cache = self.analytics_cache[cache_key]
            
            # Update counts
            cache['total_jobs'] += 1
            cache['streams'][job_data.get('stream', '')] += 1
            cache['locations'][job_data.get('location', '')] += 1
            cache['companies'][job_data.get('company', '')] += 1
            
            # Update skills
            skills = job_data.get('skills', '').split(',')
            for skill in skills:
                skill = skill.strip()
                if skill:
                    cache['skills'][skill] += 1
            
            # Add trend data
            cache['trends'].append({
                'timestamp': now.isoformat(),
                'trend_score': job_data.get('trend_score', 0),
                'popularity_score': job_data.get('popularity_score', 0)
            })
            
            # Limit cache size (keep last 24 hours)
            if len(self.analytics_cache) > 24:
                oldest_key = min(self.analytics_cache.keys())
                del self.analytics_cache[oldest_key]
                
        except Exception as e:
            logging.error(f"Error updating analytics cache: {str(e)}")
    
    def _notify_subscribers(self, job_data: dict):
        """Notify WebSocket subscribers of new job"""
        try:
            notification = {
                'type': 'new_job',
                'data': job_data,
                'timestamp': datetime.now().isoformat()
            }
            
            # In a real implementation, this would send to WebSocket clients
            # For now, we'll just log it
            logging.info(f"New job notification: {job_data.get('title', 'Unknown')} at {job_data.get('company', 'Unknown')}")
            
        except Exception as e:
            logging.error(f"Error notifying subscribers: {str(e)}")
    
    def _update_analytics(self):
        """Update analytics periodically"""
        while self.running:
            try:
                self._calculate_processing_rate()
                self._generate_insights()
                time.sleep(60)  # Update every minute
                
            except Exception as e:
                logging.error(f"Error updating analytics: {str(e)}")
                time.sleep(60)
    
    def _calculate_processing_rate(self):
        """Calculate job processing rate"""
        try:
            now = datetime.now()
            time_diff = (now - self.metrics['last_update']).total_seconds()
            
            if time_diff > 0:
                self.metrics['processing_rate'] = self.metrics['total_processed'] / time_diff
                self.metrics['last_update'] = now
                
        except Exception as e:
            logging.error(f"Error calculating processing rate: {str(e)}")
    
    def _generate_insights(self):
        """Generate real-time insights"""
        try:
            # Get recent data
            recent_cache = list(self.analytics_cache.values())[-1] if self.analytics_cache else {}
            
            if recent_cache:
                # Generate insights based on recent data
                insights = {
                    'hot_streams': sorted(recent_cache.get('streams', {}).items(), key=lambda x: x[1], reverse=True)[:5],
                    'trending_locations': sorted(recent_cache.get('locations', {}).items(), key=lambda x: x[1], reverse=True)[:5],
                    'top_companies': sorted(recent_cache.get('companies', {}).items(), key=lambda x: x[1], reverse=True)[:5],
                    'emerging_skills': sorted(recent_cache.get('skills', {}).items(), key=lambda x: x[1], reverse=True)[:10]
                }
                
                # Store insights for dashboard
                self.current_insights = insights
                
        except Exception as e:
            logging.error(f"Error generating insights: {str(e)}")
    
    def _cleanup_old_data(self):
        """Clean up old data periodically"""
        while self.running:
            try:
                # Clean up database (keep last 30 days)
                conn = sqlite3.connect(self.database_path)
                cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                
                deleted = conn.execute(
                    'DELETE FROM job_postings WHERE date_posted < ?',
                    (cutoff_date,)
                ).rowcount
                
                conn.commit()
                conn.close()
                
                if deleted > 0:
                    print(f"🧹 Cleaned up {deleted} old job postings")
                
                # Sleep for 24 hours
                time.sleep(24 * 60 * 60)
                
            except Exception as e:
                logging.error(f"Error cleaning up old data: {str(e)}")
                time.sleep(24 * 60 * 60)
    
    def get_real_time_metrics(self) -> dict:
        """Get real-time processing metrics"""
        return {
            'total_processed': self.metrics['total_processed'],
            'processing_rate': round(self.metrics['processing_rate'], 2),
            'queue_size': len(self.job_queue),
            'cache_size': len(self.analytics_cache),
            'errors': self.metrics['errors'],
            'uptime': str(datetime.now() - self.metrics['last_update']),
            'insights': getattr(self, 'current_insights', {})
        }
    
    def get_live_dashboard_data(self) -> dict:
        """Get data for live dashboard"""
        try:
            # Get recent jobs from database
            conn = sqlite3.connect(self.database_path)
            
            # Recent jobs count
            recent_jobs = conn.execute('''
                SELECT COUNT(*) FROM job_postings 
                WHERE date_posted >= date('now', '-1 day')
            ''').fetchone()[0]
            
            # Stream distribution
            stream_data = conn.execute('''
                SELECT stream, COUNT(*) as count
                FROM job_postings
                WHERE date_posted >= date('now', '-7 days')
                GROUP BY stream
                ORDER BY count DESC
                LIMIT 10
            ''').fetchall()
            
            # Location trends
            location_data = conn.execute('''
                SELECT location, COUNT(*) as count
                FROM job_postings
                WHERE date_posted >= date('now', '-7 days')
                GROUP BY location
                ORDER BY count DESC
                LIMIT 10
            ''').fetchall()
            
            # Top companies
            company_data = conn.execute('''
                SELECT company, COUNT(*) as count
                FROM job_postings
                WHERE date_posted >= date('now', '-7 days')
                GROUP BY company
                ORDER BY count DESC
                LIMIT 10
            ''').fetchall()
            
            conn.close()
            
            return {
                'recent_jobs_count': recent_jobs,
                'stream_distribution': dict(stream_data),
                'location_trends': dict(location_data),
                'top_companies': dict(company_data),
                'last_updated': datetime.now().isoformat(),
                'metrics': self.get_real_time_metrics()
            }
            
        except Exception as e:
            logging.error(f"Error getting live dashboard data: {str(e)}")
            return {}
    
    def add_job_to_queue(self, job_data: dict):
        """Add job to processing queue"""
        self.job_queue.append(job_data)
    
    def force_scrape_and_process(self):
        """Force immediate scraping and processing"""
        try:
            print("🔄 Force scraping and processing...")
            
            # Run scraping
            total_jobs, saved_jobs = self.scraper.run_daily_scraping()
            
            # Get new jobs from database
            new_jobs = self.scraper.get_jobs_from_database(limit=saved_jobs)
            
            # Add to processing queue
            for _, job in new_jobs.iterrows():
                self.add_job_to_queue(job.to_dict())
            
            print(f"✅ Added {len(new_jobs)} jobs to processing queue")
            
            return total_jobs, saved_jobs
            
        except Exception as e:
            logging.error(f"Error in force scrape and process: {str(e)}")
            return 0, 0

# Usage example
if __name__ == "__main__":
    processor = RealTimeJobProcessor()
    
    # Start real-time processing
    processor.start_real_time_processing()
    
    # Force initial scraping
    processor.force_scrape_and_process()
    
    # Keep running
    try:
        while True:
            metrics = processor.get_real_time_metrics()
            print(f"📊 Processed: {metrics['total_processed']}, Rate: {metrics['processing_rate']}/s, Queue: {metrics['queue_size']}")
            time.sleep(30)
    except KeyboardInterrupt:
        processor.stop_real_time_processing()
        print("👋 Real-time processing stopped")

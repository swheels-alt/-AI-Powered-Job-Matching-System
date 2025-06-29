"""
Data processing utilities for job posting data.
"""

import pandas as pd
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class JobDataProcessor:
    """Handles processing and validation of job posting data."""
    
    def __init__(self):
        self.required_fields = [
            'job_title', 'company_name', 'location', 'job_description'
        ]
        self.optional_fields = [
            'required_skills', 'experience_level', 'salary_range', 
            'posted_date', 'job_url', 'source_website'
        ]
    
    def clean_job_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize job data.
        
        Args:
            job_data: Raw job data dictionary
            
        Returns:
            Cleaned job data dictionary
        """
        cleaned_data = {}
        
        # Clean text fields
        for field in ['job_title', 'company_name', 'location', 'job_description']:
            if field in job_data:
                cleaned_data[field] = self._clean_text(job_data[field])
        
        # Clean optional fields
        for field in self.optional_fields:
            if field in job_data:
                cleaned_data[field] = self._clean_text(job_data[field])
        
        # Add timestamp
        cleaned_data['scraped_at'] = datetime.now().isoformat()
        
        return cleaned_data
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text data.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters that might cause issues
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        return text.strip()
    
    def validate_job_data(self, job_data: Dict[str, Any]) -> bool:
        """
        Validate job data for required fields and data quality.
        
        Args:
            job_data: Job data dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        for field in self.required_fields:
            if field not in job_data or not job_data[field]:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Check data quality
        if len(job_data.get('job_description', '')) < 50:
            logger.warning("Job description too short")
            return False
        
        if len(job_data.get('job_title', '')) < 3:
            logger.warning("Job title too short")
            return False
        
        return True
    
    def save_to_csv(self, jobs_data: List[Dict[str, Any]], filename: str) -> str:
        """
        Save job data to CSV file.
        
        Args:
            jobs_data: List of job data dictionaries
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        try:
            df = pd.DataFrame(jobs_data)
            filepath = os.path.join("data", "raw", filename)
            df.to_csv(filepath, index=False, encoding='utf-8')
            logger.info(f"Saved {len(jobs_data)} jobs to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
            raise
    
    def save_to_json(self, jobs_data: List[Dict[str, Any]], filename: str) -> str:
        """
        Save job data to JSON file.
        
        Args:
            jobs_data: List of job data dictionaries
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        try:
            filepath = os.path.join("data", "raw", filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(jobs_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(jobs_data)} jobs to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving JSON: {e}")
            raise
    
    def load_from_csv(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Load job data from CSV file.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of job data dictionaries
        """
        try:
            df = pd.read_csv(filepath)
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            raise
    
    def load_from_json(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Load job data from JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            List of job data dictionaries
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON: {e}")
            raise
    
    def merge_job_data(self, data_sources: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Merge job data from multiple sources, removing duplicates.
        
        Args:
            data_sources: List of job data lists from different sources
            
        Returns:
            Merged and deduplicated job data
        """
        all_jobs = []
        seen_urls = set()
        
        for source_data in data_sources:
            for job in source_data:
                job_url = job.get('job_url', '')
                
                # Skip if we've seen this URL before
                if job_url and job_url in seen_urls:
                    continue
                
                if self.validate_job_data(job):
                    all_jobs.append(job)
                    if job_url:
                        seen_urls.add(job_url)
        
        logger.info(f"Merged {len(all_jobs)} unique jobs from {len(data_sources)} sources")
        return all_jobs
    
    def generate_summary_stats(self, jobs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for job data.
        
        Args:
            jobs_data: List of job data dictionaries
            
        Returns:
            Dictionary with summary statistics
        """
        if not jobs_data:
            return {}
        
        df = pd.DataFrame(jobs_data)
        
        stats = {
            'total_jobs': len(jobs_data),
            'unique_companies': df['company_name'].nunique() if 'company_name' in df.columns else 0,
            'unique_locations': df['location'].nunique() if 'location' in df.columns else 0,
            'sources': df['source_website'].value_counts().to_dict() if 'source_website' in df.columns else {},
            'date_range': {
                'earliest': df['posted_date'].min() if 'posted_date' in df.columns else None,
                'latest': df['posted_date'].max() if 'posted_date' in df.columns else None
            }
        }
        
        return stats
    
    def filter_jobs(self, jobs_data: List[Dict[str, Any]], 
                   location: Optional[str] = None,
                   keywords: Optional[List[str]] = None,
                   company: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Filter jobs based on criteria.
        
        Args:
            jobs_data: List of job data dictionaries
            location: Location filter
            keywords: Keywords to search in job title and description
            company: Company name filter
            
        Returns:
            Filtered job data
        """
        filtered_jobs = jobs_data
        
        if location:
            filtered_jobs = [
                job for job in filtered_jobs 
                if location.lower() in job.get('location', '').lower()
            ]
        
        if company:
            filtered_jobs = [
                job for job in filtered_jobs 
                if company.lower() in job.get('company_name', '').lower()
            ]
        
        if keywords:
            keyword_filtered = []
            for job in filtered_jobs:
                job_text = f"{job.get('job_title', '')} {job.get('job_description', '')}".lower()
                if any(keyword.lower() in job_text for keyword in keywords):
                    keyword_filtered.append(job)
            filtered_jobs = keyword_filtered
        
        logger.info(f"Filtered {len(filtered_jobs)} jobs from {len(jobs_data)} total")
        return filtered_jobs 
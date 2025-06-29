"""
Data preprocessing pipeline for job posting data.
"""

import pandas as pd
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import os

from .text_cleaner import TextCleaner

logger = logging.getLogger(__name__)

class DataPreprocessor:
    """Handles comprehensive preprocessing of job posting data."""
    
    def __init__(self):
        self.text_cleaner = TextCleaner()
        self.required_fields = [
            'job_title', 'company_name', 'location', 'job_description'
        ]
        self.optional_fields = [
            'required_skills', 'experience_level', 'salary_range', 
            'posted_date', 'job_url', 'source_website'
        ]
    
    def preprocess_job_data(self, jobs_data: List[Dict[str, Any]], 
                          remove_stop_words: bool = False,
                          lemmatize: bool = False,
                          extract_skills: bool = True) -> List[Dict[str, Any]]:
        """
        Preprocess job data with comprehensive cleaning and normalization.
        
        Args:
            jobs_data: List of raw job data dictionaries
            remove_stop_words: Whether to remove stop words from descriptions
            lemmatize: Whether to apply lemmatization
            extract_skills: Whether to extract skills from descriptions
            
        Returns:
            List of preprocessed job data dictionaries
        """
        preprocessed_jobs = []
        
        logger.info(f"Starting preprocessing of {len(jobs_data)} jobs")
        
        for i, job in enumerate(jobs_data):
            try:
                preprocessed_job = self._preprocess_single_job(
                    job, remove_stop_words, lemmatize, extract_skills
                )
                
                if preprocessed_job:
                    preprocessed_jobs.append(preprocessed_job)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Preprocessed {i + 1}/{len(jobs_data)} jobs")
                    
            except Exception as e:
                logger.error(f"Error preprocessing job {i}: {e}")
                continue
        
        logger.info(f"Successfully preprocessed {len(preprocessed_jobs)} jobs")
        return preprocessed_jobs
    
    def _preprocess_single_job(self, job: Dict[str, Any], 
                             remove_stop_words: bool,
                             lemmatize: bool,
                             extract_skills: bool) -> Optional[Dict[str, Any]]:
        """
        Preprocess a single job entry.
        
        Args:
            job: Raw job data dictionary
            remove_stop_words: Whether to remove stop words
            lemmatize: Whether to apply lemmatization
            extract_skills: Whether to extract skills
            
        Returns:
            Preprocessed job data dictionary or None if invalid
        """
        try:
            preprocessed_job = {}
            
            # Clean and normalize job title
            if 'job_title' in job:
                preprocessed_job['job_title'] = self.text_cleaner.normalize_job_title(
                    job['job_title']
                )
            
            # Clean company name
            if 'company_name' in job:
                preprocessed_job['company_name'] = self.text_cleaner.normalize_whitespace(
                    job['company_name']
                )
            
            # Normalize location
            if 'location' in job:
                preprocessed_job['location'] = self.text_cleaner.normalize_location(
                    job['location']
                )
            
            # Clean job description
            if 'job_description' in job:
                description = job['job_description']
                
                # Clean the description
                cleaned_description = self.text_cleaner.clean_job_description(description)
                
                # Prepare for embedding
                embedding_text = self.text_cleaner.prepare_for_embedding(
                    cleaned_description, remove_stop_words, lemmatize
                )
                
                preprocessed_job['job_description'] = cleaned_description
                preprocessed_job['job_description_embedding'] = embedding_text
            
            # Extract skills from description if requested
            if extract_skills and 'job_description' in job:
                extracted_skills = self.text_cleaner.extract_skills(job['job_description'])
                preprocessed_job['extracted_skills'] = extracted_skills
            
            # Clean existing skills field
            if 'required_skills' in job:
                skills_text = job['required_skills']
                if skills_text:
                    # Clean the skills text
                    cleaned_skills = self.text_cleaner.normalize_whitespace(skills_text)
                    preprocessed_job['required_skills'] = cleaned_skills
                    
                    # Extract individual skills
                    skills_list = [skill.strip() for skill in cleaned_skills.split(',')]
                    preprocessed_job['skills_list'] = skills_list
                else:
                    preprocessed_job['required_skills'] = ""
                    preprocessed_job['skills_list'] = []
            
            # Normalize experience level
            if 'experience_level' in job:
                experience = job['experience_level'].lower()
                if 'senior' in experience:
                    preprocessed_job['experience_level'] = 'senior'
                elif 'junior' in experience or 'entry' in experience:
                    preprocessed_job['experience_level'] = 'junior'
                elif 'mid' in experience or 'intermediate' in experience:
                    preprocessed_job['experience_level'] = 'mid-level'
                else:
                    preprocessed_job['experience_level'] = 'not specified'
            
            # Clean salary range
            if 'salary_range' in job:
                salary = job['salary_range']
                if salary:
                    # Remove currency symbols and normalize
                    salary_clean = salary.replace('$', '').replace(',', '')
                    preprocessed_job['salary_range'] = salary_clean
                else:
                    preprocessed_job['salary_range'] = ""
            
            # Keep other fields as is
            for field in ['posted_date', 'job_url', 'source_website']:
                if field in job:
                    preprocessed_job[field] = job[field]
            
            # Add preprocessing metadata
            preprocessed_job['preprocessed_at'] = datetime.now().isoformat()
            preprocessed_job['preprocessing_config'] = {
                'remove_stop_words': remove_stop_words,
                'lemmatize': lemmatize,
                'extract_skills': extract_skills
            }
            
            # Validate the preprocessed job
            if self._validate_preprocessed_job(preprocessed_job):
                return preprocessed_job
            else:
                logger.warning(f"Invalid preprocessed job: missing required fields")
                return None
                
        except Exception as e:
            logger.error(f"Error preprocessing job: {e}")
            return None
    
    def _validate_preprocessed_job(self, job: Dict[str, Any]) -> bool:
        """
        Validate preprocessed job data.
        
        Args:
            job: Preprocessed job data dictionary
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        for field in self.required_fields:
            if field not in job or not job[field]:
                return False
        
        # Check data quality
        if len(job.get('job_description', '')) < 20:
            return False
        
        return True
    
    def handle_missing_data(self, jobs_data: List[Dict[str, Any]], 
                          strategy: str = 'fill_na') -> List[Dict[str, Any]]:
        """
        Handle missing data in job postings.
        
        Args:
            jobs_data: List of job data dictionaries
            strategy: Strategy for handling missing data ('fill_na', 'remove', 'interpolate')
            
        Returns:
            List of job data with missing data handled
        """
        if strategy == 'fill_na':
            return self._fill_missing_data(jobs_data)
        elif strategy == 'remove':
            return self._remove_incomplete_jobs(jobs_data)
        elif strategy == 'interpolate':
            return self._interpolate_missing_data(jobs_data)
        else:
            logger.warning(f"Unknown strategy '{strategy}', using 'fill_na'")
            return self._fill_missing_data(jobs_data)
    
    def _fill_missing_data(self, jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fill missing data with default values."""
        for job in jobs_data:
            for field in self.required_fields + self.optional_fields:
                if field not in job or not job[field]:
                    job[field] = "N/A"
        return jobs_data
    
    def _remove_incomplete_jobs(self, jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove jobs with missing required fields."""
        complete_jobs = []
        for job in jobs_data:
            if all(field in job and job[field] for field in self.required_fields):
                complete_jobs.append(job)
        return complete_jobs
    
    def _interpolate_missing_data(self, jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Interpolate missing data based on similar jobs."""
        # This is a simplified version - in production, you might use more sophisticated methods
        return self._fill_missing_data(jobs_data)
    
    def create_embedding_text(self, job: Dict[str, Any]) -> str:
        """
        Create text suitable for embedding from job data.
        
        Args:
            job: Job data dictionary
            
        Returns:
            Text prepared for embedding
        """
        embedding_parts = []
        
        # Add job title
        if 'job_title' in job:
            embedding_parts.append(job['job_title'])
        
        # Add company name
        if 'company_name' in job:
            embedding_parts.append(job['company_name'])
        
        # Add job description (use embedding version if available)
        if 'job_description_embedding' in job:
            embedding_parts.append(job['job_description_embedding'])
        elif 'job_description' in job:
            embedding_parts.append(job['job_description'])
        
        # Add skills
        if 'extracted_skills' in job and job['extracted_skills']:
            embedding_parts.append(' '.join(job['extracted_skills']))
        elif 'required_skills' in job:
            embedding_parts.append(job['required_skills'])
        
        # Add experience level
        if 'experience_level' in job:
            embedding_parts.append(job['experience_level'])
        
        return ' '.join(embedding_parts)
    
    def save_preprocessed_data(self, jobs_data: List[Dict[str, Any]], 
                             filename: str = None) -> str:
        """
        Save preprocessed job data to file.
        
        Args:
            jobs_data: List of preprocessed job data
            filename: Output filename (optional)
            
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"preprocessed_jobs_{timestamp}.json"
        
        filepath = os.path.join("data", "processed", filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save as JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved preprocessed data to {filepath}")
        return filepath
    
    def load_preprocessed_data(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Load preprocessed job data from file.
        
        Args:
            filepath: Path to preprocessed data file
            
        Returns:
            List of preprocessed job data dictionaries
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded {len(data)} preprocessed jobs from {filepath}")
        return data
    
    def generate_preprocessing_report(self, original_data: List[Dict[str, Any]], 
                                    preprocessed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a report on the preprocessing results.
        
        Args:
            original_data: Original job data
            preprocessed_data: Preprocessed job data
            
        Returns:
            Dictionary containing preprocessing statistics
        """
        report = {
            'original_count': len(original_data),
            'preprocessed_count': len(preprocessed_data),
            'removed_count': len(original_data) - len(preprocessed_data),
            'removal_rate': (len(original_data) - len(preprocessed_data)) / len(original_data) * 100,
            'average_description_length': 0,
            'skills_extraction_stats': {},
            'experience_level_distribution': {},
            'location_distribution': {}
        }
        
        if preprocessed_data:
            # Calculate average description length
            total_length = sum(len(job.get('job_description', '')) for job in preprocessed_data)
            report['average_description_length'] = total_length / len(preprocessed_data)
            
            # Skills extraction statistics
            skills_count = sum(len(job.get('extracted_skills', [])) for job in preprocessed_data)
            report['skills_extraction_stats'] = {
                'total_skills_found': skills_count,
                'average_skills_per_job': skills_count / len(preprocessed_data)
            }
            
            # Experience level distribution
            experience_levels = {}
            for job in preprocessed_data:
                level = job.get('experience_level', 'unknown')
                experience_levels[level] = experience_levels.get(level, 0) + 1
            report['experience_level_distribution'] = experience_levels
            
            # Location distribution
            locations = {}
            for job in preprocessed_data:
                location = job.get('location', 'unknown')
                locations[location] = locations.get(location, 0) + 1
            report['location_distribution'] = locations
        
        return report 
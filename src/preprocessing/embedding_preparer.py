"""
Embedding preparation utilities for job data and resume text.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import os

from .text_cleaner import TextCleaner
from .data_preprocessor import DataPreprocessor
from .resume_parser import ResumeParser

logger = logging.getLogger(__name__)

class EmbeddingPreparer:
    """Coordinates preprocessing for embedding preparation."""
    
    def __init__(self):
        self.text_cleaner = TextCleaner()
        self.data_preprocessor = DataPreprocessor()
        self.resume_parser = ResumeParser()
    
    def prepare_jobs_for_embedding(self, jobs_data: List[Dict[str, Any]], 
                                 preprocessing_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Prepare job data for embedding with comprehensive preprocessing.
        
        Args:
            jobs_data: List of raw job data dictionaries
            preprocessing_config: Configuration for preprocessing options
            
        Returns:
            List of job data prepared for embedding
        """
        if preprocessing_config is None:
            preprocessing_config = {
                'remove_stop_words': False,
                'lemmatize': False,
                'extract_skills': True,
                'missing_data_strategy': 'fill_na'
            }
        
        logger.info("Starting job data preparation for embedding")
        
        # Step 1: Handle missing data
        jobs_data = self.data_preprocessor.handle_missing_data(
            jobs_data, strategy=preprocessing_config.get('missing_data_strategy', 'fill_na')
        )
        
        # Step 2: Preprocess job data
        preprocessed_jobs = self.data_preprocessor.preprocess_job_data(
            jobs_data,
            remove_stop_words=preprocessing_config.get('remove_stop_words', False),
            lemmatize=preprocessing_config.get('lemmatize', False),
            extract_skills=preprocessing_config.get('extract_skills', True)
        )
        
        # Step 3: Create embedding text for each job
        for job in preprocessed_jobs:
            embedding_text = self.data_preprocessor.create_embedding_text(job)
            job['embedding_text'] = embedding_text
            job['embedding_prepared_at'] = datetime.now().isoformat()
        
        logger.info(f"Prepared {len(preprocessed_jobs)} jobs for embedding")
        return preprocessed_jobs
    
    def prepare_resume_for_embedding(self, resume_text: str, 
                                   preprocessing_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Prepare resume text for embedding with comprehensive preprocessing.
        
        Args:
            resume_text: Raw resume text
            preprocessing_config: Configuration for preprocessing options
            
        Returns:
            Dictionary containing prepared resume data for embedding
        """
        if preprocessing_config is None:
            preprocessing_config = {
                'remove_stop_words': False,
                'lemmatize': False,
                'include_sections': ['summary', 'experience', 'skills', 'education', 'projects']
            }
        
        logger.info("Starting resume preparation for embedding")
        
        # Step 1: Parse resume text
        parsed_resume = self.resume_parser.parse_resume_text(resume_text)
        
        # Step 2: Create embedding text
        embedding_text = self.resume_parser.create_resume_embedding_text(
            parsed_resume, 
            include_sections=preprocessing_config.get('include_sections')
        )
        
        # Step 3: Apply additional preprocessing
        final_embedding_text = self.text_cleaner.prepare_for_embedding(
            embedding_text,
            remove_stop_words=preprocessing_config.get('remove_stop_words', False),
            lemmatize=preprocessing_config.get('lemmatize', False)
        )
        
        # Step 4: Create final resume data
        prepared_resume = {
            'raw_text': resume_text,
            'parsed_resume': parsed_resume,
            'embedding_text': final_embedding_text,
            'embedding_prepared_at': datetime.now().isoformat(),
            'preprocessing_config': preprocessing_config
        }
        
        logger.info("Resume preparation completed")
        return prepared_resume
    
    def create_embedding_batch(self, jobs_data: List[Dict[str, Any]], 
                             resume_text: str = None,
                             preprocessing_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a batch of data prepared for embedding.
        
        Args:
            jobs_data: List of raw job data
            resume_text: Raw resume text (optional)
            preprocessing_config: Configuration for preprocessing
            
        Returns:
            Dictionary containing all data prepared for embedding
        """
        if preprocessing_config is None:
            preprocessing_config = {
                'jobs': {
                    'remove_stop_words': False,
                    'lemmatize': False,
                    'extract_skills': True,
                    'missing_data_strategy': 'fill_na'
                },
                'resume': {
                    'remove_stop_words': False,
                    'lemmatize': False,
                    'include_sections': ['summary', 'experience', 'skills', 'education', 'projects']
                }
            }
        
        logger.info("Creating embedding batch")
        
        # Prepare jobs
        prepared_jobs = self.prepare_jobs_for_embedding(
            jobs_data, preprocessing_config.get('jobs', {})
        )
        
        # Prepare resume if provided
        prepared_resume = None
        if resume_text:
            prepared_resume = self.prepare_resume_for_embedding(
                resume_text, preprocessing_config.get('resume', {})
            )
        
        # Create batch
        embedding_batch = {
            'jobs': prepared_jobs,
            'resume': prepared_resume,
            'batch_created_at': datetime.now().isoformat(),
            'preprocessing_config': preprocessing_config,
            'statistics': self._generate_batch_statistics(prepared_jobs, prepared_resume)
        }
        
        logger.info("Embedding batch created successfully")
        return embedding_batch
    
    def _generate_batch_statistics(self, prepared_jobs: List[Dict[str, Any]], 
                                 prepared_resume: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate statistics for the embedding batch.
        
        Args:
            prepared_jobs: List of prepared job data
            prepared_resume: Prepared resume data
            
        Returns:
            Dictionary containing batch statistics
        """
        stats = {
            'total_jobs': len(prepared_jobs),
            'jobs_with_skills': 0,
            'average_job_description_length': 0,
            'resume_included': prepared_resume is not None
        }
        
        if prepared_jobs:
            # Calculate job statistics
            total_description_length = 0
            for job in prepared_jobs:
                description = job.get('job_description', '')
                total_description_length += len(description)
                
                if job.get('extracted_skills'):
                    stats['jobs_with_skills'] += 1
            
            stats['average_job_description_length'] = total_description_length / len(prepared_jobs)
        
        if prepared_resume:
            # Add resume statistics
            resume_stats = self.resume_parser.generate_resume_summary(
                prepared_resume['parsed_resume']
            )
            stats['resume_statistics'] = resume_stats
        
        return stats
    
    def save_embedding_batch(self, embedding_batch: Dict[str, Any], 
                           filename: str = None) -> str:
        """
        Save embedding batch to file.
        
        Args:
            embedding_batch: Embedding batch dictionary
            filename: Output filename (optional)
            
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"embedding_batch_{timestamp}.json"
        
        filepath = os.path.join("data", "processed", filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save as JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(embedding_batch, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved embedding batch to {filepath}")
        return filepath
    
    def load_embedding_batch(self, filepath: str) -> Dict[str, Any]:
        """
        Load embedding batch from file.
        
        Args:
            filepath: Path to embedding batch file
            
        Returns:
            Embedding batch dictionary
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            batch = json.load(f)
        
        logger.info(f"Loaded embedding batch from {filepath}")
        return batch
    
    def extract_embedding_texts(self, embedding_batch: Dict[str, Any]) -> Tuple[List[str], Optional[str]]:
        """
        Extract embedding texts from batch.
        
        Args:
            embedding_batch: Embedding batch dictionary
            
        Returns:
            Tuple of (job_embedding_texts, resume_embedding_text)
        """
        # Extract job embedding texts
        job_texts = []
        for job in embedding_batch.get('jobs', []):
            if 'embedding_text' in job:
                job_texts.append(job['embedding_text'])
        
        # Extract resume embedding text
        resume_text = None
        if embedding_batch.get('resume') and 'embedding_text' in embedding_batch['resume']:
            resume_text = embedding_batch['resume']['embedding_text']
        
        return job_texts, resume_text
    
    def validate_embedding_batch(self, embedding_batch: Dict[str, Any]) -> bool:
        """
        Validate embedding batch structure and content.
        
        Args:
            embedding_batch: Embedding batch dictionary
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required keys
            required_keys = ['jobs', 'batch_created_at', 'preprocessing_config', 'statistics']
            for key in required_keys:
                if key not in embedding_batch:
                    logger.error(f"Missing required key: {key}")
                    return False
            
            # Check jobs
            jobs = embedding_batch['jobs']
            if not isinstance(jobs, list):
                logger.error("Jobs must be a list")
                return False
            
            # Check each job has embedding text
            for i, job in enumerate(jobs):
                if 'embedding_text' not in job:
                    logger.error(f"Job {i} missing embedding_text")
                    return False
                if not job['embedding_text']:
                    logger.error(f"Job {i} has empty embedding_text")
                    return False
            
            # Check resume if present
            resume = embedding_batch.get('resume')
            if resume and 'embedding_text' not in resume:
                logger.error("Resume missing embedding_text")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating embedding batch: {e}")
            return False
    
    def generate_preprocessing_report(self, original_jobs: List[Dict[str, Any]], 
                                    embedding_batch: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive preprocessing report.
        
        Args:
            original_jobs: Original job data
            embedding_batch: Embedding batch dictionary
            
        Returns:
            Dictionary containing preprocessing report
        """
        report = {
            'preprocessing_summary': {
                'original_jobs_count': len(original_jobs),
                'preprocessed_jobs_count': len(embedding_batch['jobs']),
                'resume_included': embedding_batch.get('resume') is not None,
                'preprocessing_config': embedding_batch['preprocessing_config']
            },
            'job_preprocessing_stats': self.data_preprocessor.generate_preprocessing_report(
                original_jobs, embedding_batch['jobs']
            ),
            'embedding_batch_stats': embedding_batch['statistics']
        }
        
        # Add resume statistics if present
        if embedding_batch.get('resume'):
            resume_summary = self.resume_parser.generate_resume_summary(
                embedding_batch['resume']['parsed_resume']
            )
            report['resume_preprocessing_stats'] = resume_summary
        
        return report 
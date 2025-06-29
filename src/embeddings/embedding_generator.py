"""
Main embedding generator that coordinates the complete embedding pipeline.
"""

import os
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .openai_embedder import OpenAIEmbedder
from .embedding_manager import EmbeddingManager
from .similarity_calculator import SimilarityCalculator

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Main class that coordinates embedding generation, storage, and similarity calculations."""
    
    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small", 
                 storage_dir: str = "data/embeddings"):
        """
        Initialize embedding generator.
        
        Args:
            api_key: OpenAI API key
            model: Embedding model to use
            storage_dir: Directory for storing embeddings
        """
        self.embedder = OpenAIEmbedder(api_key, model)
        self.manager = EmbeddingManager(storage_dir)
        self.calculator = SimilarityCalculator()
        
        logger.info(f"Initialized embedding generator with model: {model}")
    
    def generate_job_embeddings(self, jobs_data: List[Dict[str, Any]], 
                              batch_size: int = 100) -> List[str]:
        """
        Generate embeddings for job data.
        
        Args:
            jobs_data: List of preprocessed job data
            batch_size: Batch size for embedding generation
            
        Returns:
            List of embedding IDs
        """
        if not jobs_data:
            logger.warning("No job data provided for embedding generation")
            return []
        
        logger.info(f"Starting job embedding generation for {len(jobs_data)} jobs")
        
        # Extract embedding texts
        embedding_texts = []
        valid_jobs = []
        
        for job in jobs_data:
            embedding_text = job.get('embedding_text', '')
            if embedding_text:
                embedding_texts.append(embedding_text)
                valid_jobs.append(job)
            else:
                logger.warning(f"Job missing embedding_text: {job.get('job_title', 'Unknown')}")
        
        if not embedding_texts:
            logger.error("No valid embedding texts found in job data")
            return []
        
        logger.info(f"Generating embeddings for {len(embedding_texts)} valid jobs")
        
        try:
            # Generate embeddings
            embeddings = self.embedder.embed_batch(embedding_texts, batch_size)
            
            # Save embeddings
            embedding_ids = self.manager.save_job_embeddings(valid_jobs, embeddings, self.embedder.model)
            
            logger.info(f"Successfully generated and saved {len(embedding_ids)} job embeddings")
            return embedding_ids
            
        except Exception as e:
            logger.error(f"Failed to generate job embeddings: {e}")
            raise
    
    def generate_resume_embedding(self, resume_text: str, 
                                metadata: Dict[str, Any] = None) -> str:
        """
        Generate embedding for resume text.
        
        Args:
            resume_text: Resume text to embed
            metadata: Additional metadata
            
        Returns:
            Embedding ID
        """
        if not resume_text or not resume_text.strip():
            logger.warning("Empty resume text provided for embedding")
            return ""
        
        logger.info("Starting resume embedding generation")
        
        try:
            # Generate embedding
            embedding = self.embedder.embed_text(resume_text)
            
            if not embedding:
                logger.error("Failed to generate resume embedding")
                return ""
            
            # Save embedding
            embedding_id = self.manager.save_resume_embedding(
                resume_text, embedding, self.embedder.model, metadata
            )
            
            logger.info(f"Successfully generated and saved resume embedding: {embedding_id}")
            return embedding_id
            
        except Exception as e:
            logger.error(f"Failed to generate resume embedding: {e}")
            raise
    
    def generate_embeddings_from_batch(self, embedding_batch: Dict[str, Any], 
                                     batch_size: int = 100) -> Dict[str, Any]:
        """
        Generate embeddings from a preprocessing batch.
        
        Args:
            embedding_batch: Embedding batch from preprocessing
            batch_size: Batch size for job embedding generation
            
        Returns:
            Dictionary with embedding results
        """
        logger.info("Starting embedding generation from preprocessing batch")
        
        results = {
            'job_embedding_ids': [],
            'resume_embedding_id': "",
            'generated_at': datetime.now().isoformat(),
            'model': self.embedder.model,
            'usage_stats': {}
        }
        
        try:
            # Generate job embeddings
            jobs_data = embedding_batch.get('jobs', [])
            if jobs_data:
                job_embedding_ids = self.generate_job_embeddings(jobs_data, batch_size)
                results['job_embedding_ids'] = job_embedding_ids
            
            # Generate resume embedding
            resume_data = embedding_batch.get('resume')
            if resume_data and 'embedding_text' in resume_data:
                resume_embedding_id = self.generate_resume_embedding(
                    resume_data['embedding_text'],
                    metadata={'parsed_resume': resume_data.get('parsed_resume', {})}
                )
                results['resume_embedding_id'] = resume_embedding_id
            
            # Get usage statistics
            results['usage_stats'] = self.embedder.get_usage_stats()
            
            logger.info("Embedding generation from batch completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings from batch: {e}")
            raise
    
    def find_similar_jobs(self, resume_embedding_id: str, top_k: int = 10, 
                         similarity_metric: str = 'cosine_similarity') -> List[Dict[str, Any]]:
        """
        Find jobs similar to a resume embedding.
        
        Args:
            resume_embedding_id: Resume embedding ID
            top_k: Number of top similar jobs to return
            similarity_metric: Similarity metric to use
            
        Returns:
            List of similar job results with similarity scores
        """
        logger.info(f"Finding similar jobs for resume {resume_embedding_id}")
        
        # Load resume embedding
        resume_data = self.manager.load_embedding(resume_embedding_id)
        if not resume_data:
            logger.error(f"Resume embedding {resume_embedding_id} not found")
            return []
        
        resume_embedding = resume_data['embedding']
        
        # Get all job embeddings
        job_embeddings_data = self.manager.get_job_embeddings()
        if not job_embeddings_data:
            logger.warning("No job embeddings found")
            return []
        
        # Extract embeddings and metadata
        job_embeddings = []
        job_metadata = []
        
        for embedding_id, embedding_data in job_embeddings_data:
            if embedding_data and embedding_data.get('embedding'):
                job_embeddings.append(embedding_data['embedding'])
                job_metadata.append({
                    'embedding_id': embedding_id,
                    'text': embedding_data.get('text', ''),
                    'job_title': embedding_data.get('metadata', {}).get('job_title', ''),
                    'company_name': embedding_data.get('metadata', {}).get('company_name', ''),
                    'location': embedding_data.get('metadata', {}).get('location', ''),
                    'job_index': embedding_data.get('metadata', {}).get('job_index', -1)
                })
        
        if not job_embeddings:
            logger.warning("No valid job embeddings found")
            return []
        
        # Find most similar jobs
        similar_indices = self.calculator.find_most_similar(
            resume_embedding, job_embeddings, similarity_metric, top_k
        )
        
        # Prepare results
        similar_jobs = []
        for index, similarity_score in similar_indices:
            if index < len(job_metadata):
                job_result = job_metadata[index].copy()
                job_result['similarity_score'] = similarity_score
                job_result['similarity_metric'] = similarity_metric
                similar_jobs.append(job_result)
        
        logger.info(f"Found {len(similar_jobs)} similar jobs")
        return similar_jobs
    
    def calculate_job_similarities(self, similarity_metric: str = 'cosine_similarity') -> np.ndarray:
        """
        Calculate similarity matrix for all job embeddings.
        
        Args:
            similarity_metric: Similarity metric to use
            
        Returns:
            Similarity matrix as numpy array
        """
        logger.info("Calculating job similarity matrix")
        
        # Get all job embeddings
        job_embeddings_data = self.manager.get_job_embeddings()
        if not job_embeddings_data:
            logger.warning("No job embeddings found")
            return np.array([])
        
        # Extract embeddings
        job_embeddings = []
        for embedding_id, embedding_data in job_embeddings_data:
            if embedding_data and embedding_data.get('embedding'):
                job_embeddings.append(embedding_data['embedding'])
        
        if not job_embeddings:
            logger.warning("No valid job embeddings found")
            return np.array([])
        
        # Calculate similarity matrix
        similarity_matrix = self.calculator.batch_similarity_matrix(job_embeddings, similarity_metric)
        
        logger.info(f"Calculated similarity matrix: {similarity_matrix.shape}")
        return similarity_matrix
    
    def get_embedding_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive embedding statistics.
        
        Returns:
            Dictionary with embedding statistics
        """
        # Get storage statistics
        storage_stats = self.manager.get_storage_stats()
        
        # Get job embeddings for analysis
        job_embeddings_data = self.manager.get_job_embeddings()
        job_embeddings = []
        for embedding_id, embedding_data in job_embeddings_data:
            if embedding_data and embedding_data.get('embedding'):
                job_embeddings.append(embedding_data['embedding'])
        
        # Get resume embedding for analysis
        resume_data = self.manager.get_resume_embedding()
        resume_embedding = []
        if resume_data:
            embedding_data = resume_data[1]
            if embedding_data and embedding_data.get('embedding'):
                resume_embedding = embedding_data['embedding']
        
        # Calculate embedding statistics
        job_stats = self.calculator.calculate_embedding_statistics(job_embeddings)
        resume_stats = self.calculator.calculate_embedding_statistics([resume_embedding]) if resume_embedding else {}
        
        # Get API usage statistics
        api_stats = self.embedder.get_usage_stats()
        
        return {
            'storage': storage_stats,
            'job_embeddings': job_stats,
            'resume_embedding': resume_stats,
            'api_usage': api_stats,
            'model': self.embedder.model
        }
    
    def export_embeddings_report(self, output_file: str = None) -> str:
        """
        Export a comprehensive embeddings report.
        
        Args:
            output_file: Output file path (optional)
            
        Returns:
            Path to exported report
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"embedding_report_{timestamp}.json"
        
        # Get statistics
        stats = self.get_embedding_statistics()
        
        # Get job embeddings with metadata
        job_embeddings_data = self.manager.get_job_embeddings()
        jobs_info = []
        
        for embedding_id, embedding_data in job_embeddings_data:
            if embedding_data:
                job_info = {
                    'embedding_id': embedding_id,
                    'job_title': embedding_data.get('metadata', {}).get('job_title', ''),
                    'company_name': embedding_data.get('metadata', {}).get('company_name', ''),
                    'location': embedding_data.get('metadata', {}).get('location', ''),
                    'dimension': embedding_data.get('dimension', 0),
                    'created_at': embedding_data.get('created_at', ''),
                    'text_preview': embedding_data.get('text', '')[:200] + "..." if len(embedding_data.get('text', '')) > 200 else embedding_data.get('text', '')
                }
                jobs_info.append(job_info)
        
        # Get resume embedding info
        resume_info = {}
        resume_data = self.manager.get_resume_embedding()
        if resume_data:
            embedding_id, embedding_data = resume_data
            resume_info = {
                'embedding_id': embedding_id,
                'dimension': embedding_data.get('dimension', 0),
                'created_at': embedding_data.get('created_at', ''),
                'text_preview': embedding_data.get('text', '')[:200] + "..." if len(embedding_data.get('text', '')) > 200 else embedding_data.get('text', '')
            }
        
        # Create report
        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': stats,
            'jobs': jobs_info,
            'resume': resume_info,
            'model': self.embedder.model
        }
        
        # Save report
        try:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Exported embedding report to {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Failed to export embedding report: {e}")
            raise
    
    def test_embedding_pipeline(self) -> bool:
        """
        Test the complete embedding pipeline.
        
        Returns:
            True if all tests pass, False otherwise
        """
        logger.info("Testing embedding pipeline")
        
        try:
            # Test API connection
            if not self.embedder.test_connection():
                logger.error("API connection test failed")
                return False
            
            # Test embedding generation
            test_text = "Software Engineer with Python and JavaScript experience"
            test_embedding = self.embedder.embed_text(test_text)
            if not test_embedding:
                logger.error("Embedding generation test failed")
                return False
            
            # Test embedding storage
            test_embedding_id = self.manager.save_embedding(
                test_text, test_embedding, self.embedder.model, {'test': True}
            )
            if not test_embedding_id:
                logger.error("Embedding storage test failed")
                return False
            
            # Test embedding retrieval
            retrieved_data = self.manager.load_embedding(test_embedding_id)
            if not retrieved_data:
                logger.error("Embedding retrieval test failed")
                return False
            
            # Test similarity calculation
            similarity = self.calculator.cosine_similarity(test_embedding, test_embedding)
            if similarity != 1.0:
                logger.error("Similarity calculation test failed")
                return False
            
            # Clean up test embedding
            self.manager.delete_embedding(test_embedding_id)
            
            logger.info("All embedding pipeline tests passed")
            return True
            
        except Exception as e:
            logger.error(f"Embedding pipeline test failed: {e}")
            return False 
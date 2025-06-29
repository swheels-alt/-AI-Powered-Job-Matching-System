"""
Embedding storage and management utilities.
"""

import os
import json
import pickle
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Manages storage, retrieval, and operations on embeddings."""
    
    def __init__(self, storage_dir: str = "data/embeddings"):
        """
        Initialize embedding manager.
        
        Args:
            storage_dir: Directory to store embeddings
        """
        self.storage_dir = storage_dir
        self.ensure_storage_dir()
        
        # Metadata file
        self.metadata_file = os.path.join(storage_dir, "metadata.json")
        self.metadata = self.load_metadata()
        
        logger.info(f"Initialized embedding manager with storage directory: {storage_dir}")
    
    def ensure_storage_dir(self):
        """Ensure storage directory exists."""
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def load_metadata(self) -> Dict[str, Any]:
        """
        Load metadata from file.
        
        Returns:
            Metadata dictionary
        """
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)
                logger.info(f"Loaded metadata: {len(metadata.get('embeddings', {}))} embeddings tracked")
                return metadata
            except Exception as e:
                logger.warning(f"Failed to load metadata: {e}")
        
        return {
            'embeddings': {},
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
    
    def save_metadata(self):
        """Save metadata to file."""
        self.metadata['last_updated'] = datetime.now().isoformat()
        
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            logger.debug("Metadata saved successfully")
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def _generate_embedding_id(self, text: str, model: str) -> str:
        """
        Generate a unique ID for an embedding based on text and model.
        
        Args:
            text: Text that was embedded
            model: Model used for embedding
            
        Returns:
            Unique embedding ID
        """
        # Create a hash of the text and model
        content = f"{text[:100]}_{model}"  # Use first 100 chars for efficiency
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_embedding_filename(self, embedding_id: str) -> str:
        """
        Get filename for embedding storage.
        
        Args:
            embedding_id: Unique embedding ID
            
        Returns:
            Filename for the embedding
        """
        return os.path.join(self.storage_dir, f"{embedding_id}.pkl")
    
    def save_embedding(self, text: str, embedding: List[float], model: str, 
                      metadata: Dict[str, Any] = None) -> str:
        """
        Save an embedding to storage.
        
        Args:
            text: Original text that was embedded
            embedding: Embedding vector
            model: Model used for embedding
            metadata: Additional metadata
            
        Returns:
            Embedding ID
        """
        embedding_id = self._generate_embedding_id(text, model)
        filename = self._get_embedding_filename(embedding_id)
        
        # Prepare embedding data
        embedding_data = {
            'text': text,
            'embedding': embedding,
            'model': model,
            'dimension': len(embedding),
            'created_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        # Save embedding file
        try:
            with open(filename, 'wb') as f:
                pickle.dump(embedding_data, f)
            
            # Update metadata
            self.metadata['embeddings'][embedding_id] = {
                'text_preview': text[:100] + "..." if len(text) > 100 else text,
                'model': model,
                'dimension': len(embedding),
                'created_at': embedding_data['created_at'],
                'filename': filename
            }
            self.save_metadata()
            
            logger.info(f"Saved embedding {embedding_id} ({len(embedding)} dimensions)")
            return embedding_id
            
        except Exception as e:
            logger.error(f"Failed to save embedding {embedding_id}: {e}")
            raise
    
    def load_embedding(self, embedding_id: str) -> Optional[Dict[str, Any]]:
        """
        Load an embedding from storage.
        
        Args:
            embedding_id: Unique embedding ID
            
        Returns:
            Embedding data dictionary or None if not found
        """
        if embedding_id not in self.metadata['embeddings']:
            logger.warning(f"Embedding {embedding_id} not found in metadata")
            return None
        
        filename = self._get_embedding_filename(embedding_id)
        
        if not os.path.exists(filename):
            logger.warning(f"Embedding file not found: {filename}")
            return None
        
        try:
            with open(filename, 'rb') as f:
                embedding_data = pickle.load(f)
            logger.debug(f"Loaded embedding {embedding_id}")
            return embedding_data
        except Exception as e:
            logger.error(f"Failed to load embedding {embedding_id}: {e}")
            return None
    
    def save_job_embeddings(self, jobs_data: List[Dict[str, Any]], 
                           embeddings: List[List[float]], model: str) -> List[str]:
        """
        Save embeddings for multiple jobs.
        
        Args:
            jobs_data: List of job data dictionaries
            embeddings: List of embedding vectors
            model: Model used for embedding
            
        Returns:
            List of embedding IDs
        """
        if len(jobs_data) != len(embeddings):
            raise ValueError("Number of jobs and embeddings must match")
        
        embedding_ids = []
        
        for i, (job, embedding) in enumerate(zip(jobs_data, embeddings)):
            if not embedding:  # Skip empty embeddings
                logger.warning(f"Skipping empty embedding for job {i}")
                continue
            
            # Use embedding text from job
            embedding_text = job.get('embedding_text', '')
            if not embedding_text:
                logger.warning(f"No embedding_text found for job {i}")
                continue
            
            # Additional metadata
            metadata = {
                'job_title': job.get('job_title', ''),
                'company_name': job.get('company_name', ''),
                'location': job.get('location', ''),
                'job_index': i
            }
            
            try:
                embedding_id = self.save_embedding(embedding_text, embedding, model, metadata)
                embedding_ids.append(embedding_id)
            except Exception as e:
                logger.error(f"Failed to save embedding for job {i}: {e}")
        
        logger.info(f"Saved {len(embedding_ids)} job embeddings")
        return embedding_ids
    
    def save_resume_embedding(self, resume_text: str, embedding: List[float], 
                            model: str, metadata: Dict[str, Any] = None) -> str:
        """
        Save resume embedding.
        
        Args:
            resume_text: Resume text that was embedded
            embedding: Embedding vector
            model: Model used for embedding
            metadata: Additional metadata
            
        Returns:
            Embedding ID
        """
        if not metadata:
            metadata = {'type': 'resume'}
        else:
            metadata['type'] = 'resume'
        
        embedding_id = self.save_embedding(resume_text, embedding, model, metadata)
        logger.info(f"Saved resume embedding: {embedding_id}")
        return embedding_id
    
    def get_all_embeddings(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all stored embeddings metadata.
        
        Returns:
            Dictionary of embedding metadata
        """
        return self.metadata['embeddings']
    
    def get_job_embeddings(self) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Get all job embeddings.
        
        Returns:
            List of (embedding_id, embedding_data) tuples
        """
        job_embeddings = []
        
        for embedding_id, metadata in self.metadata['embeddings'].items():
            embedding_data = self.load_embedding(embedding_id)
            if embedding_data and embedding_data.get('metadata', {}).get('type') != 'resume':
                job_embeddings.append((embedding_id, embedding_data))
        
        return job_embeddings
    
    def get_resume_embedding(self) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Get resume embedding.
        
        Returns:
            (embedding_id, embedding_data) tuple or None if not found
        """
        for embedding_id, metadata in self.metadata['embeddings'].items():
            embedding_data = self.load_embedding(embedding_id)
            if embedding_data and embedding_data.get('metadata', {}).get('type') == 'resume':
                return (embedding_id, embedding_data)
        
        return None
    
    def delete_embedding(self, embedding_id: str) -> bool:
        """
        Delete an embedding from storage.
        
        Args:
            embedding_id: Unique embedding ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if embedding_id not in self.metadata['embeddings']:
            logger.warning(f"Embedding {embedding_id} not found in metadata")
            return False
        
        filename = self._get_embedding_filename(embedding_id)
        
        try:
            # Delete file
            if os.path.exists(filename):
                os.remove(filename)
            
            # Remove from metadata
            del self.metadata['embeddings'][embedding_id]
            self.save_metadata()
            
            logger.info(f"Deleted embedding {embedding_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete embedding {embedding_id}: {e}")
            return False
    
    def clear_all_embeddings(self):
        """Clear all stored embeddings."""
        try:
            # Delete all embedding files
            for embedding_id in list(self.metadata['embeddings'].keys()):
                self.delete_embedding(embedding_id)
            
            logger.info("Cleared all embeddings")
        except Exception as e:
            logger.error(f"Failed to clear embeddings: {e}")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Dictionary with storage statistics
        """
        total_embeddings = len(self.metadata['embeddings'])
        job_embeddings = len([e for e in self.metadata['embeddings'].values() 
                            if e.get('metadata', {}).get('type') != 'resume'])
        resume_embeddings = total_embeddings - job_embeddings
        
        # Calculate total storage size
        total_size = 0
        for embedding_id in self.metadata['embeddings']:
            filename = self._get_embedding_filename(embedding_id)
            if os.path.exists(filename):
                total_size += os.path.getsize(filename)
        
        return {
            'total_embeddings': total_embeddings,
            'job_embeddings': job_embeddings,
            'resume_embeddings': resume_embeddings,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'created_at': self.metadata.get('created_at'),
            'last_updated': self.metadata.get('last_updated')
        }
    
    def export_embeddings(self, output_file: str, format: str = 'json'):
        """
        Export all embeddings to a file.
        
        Args:
            output_file: Output file path
            format: Export format ('json' or 'pickle')
        """
        all_embeddings = {}
        
        for embedding_id in self.metadata['embeddings']:
            embedding_data = self.load_embedding(embedding_id)
            if embedding_data:
                all_embeddings[embedding_id] = embedding_data
        
        try:
            if format.lower() == 'json':
                # Convert numpy arrays to lists for JSON serialization
                export_data = {}
                for embedding_id, data in all_embeddings.items():
                    export_data[embedding_id] = {
                        'text': data['text'],
                        'embedding': data['embedding'],
                        'model': data['model'],
                        'dimension': data['dimension'],
                        'created_at': data['created_at'],
                        'metadata': data['metadata']
                    }
                
                with open(output_file, 'w') as f:
                    json.dump(export_data, f, indent=2)
            
            elif format.lower() == 'pickle':
                with open(output_file, 'wb') as f:
                    pickle.dump(all_embeddings, f)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Exported {len(all_embeddings)} embeddings to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to export embeddings: {e}")
            raise 
"""
Similarity calculation utilities for embeddings.
"""

import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from scipy.spatial.distance import cosine, euclidean
import math

logger = logging.getLogger(__name__)

class SimilarityCalculator:
    """Calculates various similarity metrics between embeddings."""
    
    def __init__(self):
        """Initialize similarity calculator."""
        logger.info("Initialized similarity calculator")
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0 to 1, where 1 is most similar)
        """
        if not embedding1 or not embedding2:
            return 0.0
        
        if len(embedding1) != len(embedding2):
            logger.warning("Embedding dimensions don't match")
            return 0.0
        
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1, dtype=np.float64)
            vec2 = np.array(embedding2, dtype=np.float64)
            
            # Calculate cosine similarity
            similarity = 1 - cosine(vec1, vec2)
            
            # Handle NaN values
            if np.isnan(similarity):
                return 0.0
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def euclidean_distance(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate Euclidean distance between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Euclidean distance (0 is most similar)
        """
        if not embedding1 or not embedding2:
            return float('inf')
        
        if len(embedding1) != len(embedding2):
            logger.warning("Embedding dimensions don't match")
            return float('inf')
        
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1, dtype=np.float64)
            vec2 = np.array(embedding2, dtype=np.float64)
            
            # Calculate Euclidean distance
            distance = euclidean(vec1, vec2)
            
            # Handle NaN values
            if np.isnan(distance):
                return float('inf')
            
            return float(distance)
            
        except Exception as e:
            logger.error(f"Error calculating Euclidean distance: {e}")
            return float('inf')
    
    def euclidean_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate Euclidean similarity (converted from distance).
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Euclidean similarity score (0 to 1, where 1 is most similar)
        """
        distance = self.euclidean_distance(embedding1, embedding2)
        
        if distance == float('inf'):
            return 0.0
        
        # Convert distance to similarity (1 / (1 + distance))
        similarity = 1 / (1 + distance)
        return similarity
    
    def dot_product_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate dot product similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Dot product similarity score
        """
        if not embedding1 or not embedding2:
            return 0.0
        
        if len(embedding1) != len(embedding2):
            logger.warning("Embedding dimensions don't match")
            return 0.0
        
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1, dtype=np.float64)
            vec2 = np.array(embedding2, dtype=np.float64)
            
            # Calculate dot product
            dot_product = np.dot(vec1, vec2)
            
            # Handle NaN values
            if np.isnan(dot_product):
                return 0.0
            
            return float(dot_product)
            
        except Exception as e:
            logger.error(f"Error calculating dot product similarity: {e}")
            return 0.0
    
    def manhattan_distance(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate Manhattan distance between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Manhattan distance (0 is most similar)
        """
        if not embedding1 or not embedding2:
            return float('inf')
        
        if len(embedding1) != len(embedding2):
            logger.warning("Embedding dimensions don't match")
            return float('inf')
        
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1, dtype=np.float64)
            vec2 = np.array(embedding2, dtype=np.float64)
            
            # Calculate Manhattan distance
            distance = np.sum(np.abs(vec1 - vec2))
            
            # Handle NaN values
            if np.isnan(distance):
                return float('inf')
            
            return float(distance)
            
        except Exception as e:
            logger.error(f"Error calculating Manhattan distance: {e}")
            return float('inf')
    
    def calculate_all_similarities(self, embedding1: List[float], 
                                 embedding2: List[float]) -> Dict[str, float]:
        """
        Calculate all similarity metrics between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Dictionary with all similarity metrics
        """
        return {
            'cosine_similarity': self.cosine_similarity(embedding1, embedding2),
            'euclidean_distance': self.euclidean_distance(embedding1, embedding2),
            'euclidean_similarity': self.euclidean_similarity(embedding1, embedding2),
            'dot_product': self.dot_product_similarity(embedding1, embedding2),
            'manhattan_distance': self.manhattan_distance(embedding1, embedding2)
        }
    
    def find_most_similar(self, query_embedding: List[float], 
                         candidate_embeddings: List[List[float]], 
                         metric: str = 'cosine_similarity',
                         top_k: int = 5) -> List[Tuple[int, float]]:
        """
        Find the most similar embeddings to a query embedding.
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embedding vectors
            metric: Similarity metric to use
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples, sorted by similarity
        """
        if not query_embedding or not candidate_embeddings:
            return []
        
        similarities = []
        
        for i, candidate in enumerate(candidate_embeddings):
            if not candidate:
                continue
            
            if metric == 'cosine_similarity':
                score = self.cosine_similarity(query_embedding, candidate)
            elif metric == 'euclidean_similarity':
                score = self.euclidean_similarity(query_embedding, candidate)
            elif metric == 'dot_product':
                score = self.dot_product_similarity(query_embedding, candidate)
            elif metric == 'euclidean_distance':
                # For distance metrics, we want to minimize
                score = -self.euclidean_distance(query_embedding, candidate)
            elif metric == 'manhattan_distance':
                # For distance metrics, we want to minimize
                score = -self.manhattan_distance(query_embedding, candidate)
            else:
                logger.warning(f"Unknown metric: {metric}, using cosine similarity")
                score = self.cosine_similarity(query_embedding, candidate)
            
            similarities.append((i, score))
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k results
        return similarities[:top_k]
    
    def batch_similarity_matrix(self, embeddings: List[List[float]], 
                              metric: str = 'cosine_similarity') -> np.ndarray:
        """
        Calculate similarity matrix for a batch of embeddings.
        
        Args:
            embeddings: List of embedding vectors
            metric: Similarity metric to use
            
        Returns:
            Similarity matrix as numpy array
        """
        if not embeddings:
            return np.array([])
        
        # Filter out empty embeddings
        valid_embeddings = [emb for emb in embeddings if emb]
        
        if not valid_embeddings:
            return np.array([])
        
        try:
            # Convert to numpy array
            embedding_matrix = np.array(valid_embeddings, dtype=np.float64)
            
            if metric == 'cosine_similarity':
                # Use sklearn's cosine_similarity for efficiency
                similarity_matrix = cosine_similarity(embedding_matrix)
            elif metric == 'euclidean_distance':
                # Use sklearn's euclidean_distances for efficiency
                distance_matrix = euclidean_distances(embedding_matrix)
                # Convert distances to similarities
                similarity_matrix = 1 / (1 + distance_matrix)
            else:
                # For other metrics, calculate pairwise
                n = len(valid_embeddings)
                similarity_matrix = np.zeros((n, n))
                
                for i in range(n):
                    for j in range(n):
                        if i == j:
                            similarity_matrix[i, j] = 1.0
                        else:
                            if metric == 'dot_product':
                                similarity_matrix[i, j] = self.dot_product_similarity(
                                    valid_embeddings[i], valid_embeddings[j]
                                )
                            elif metric == 'manhattan_distance':
                                distance = self.manhattan_distance(
                                    valid_embeddings[i], valid_embeddings[j]
                                )
                                similarity_matrix[i, j] = 1 / (1 + distance)
                            else:
                                similarity_matrix[i, j] = self.cosine_similarity(
                                    valid_embeddings[i], valid_embeddings[j]
                                )
            
            return similarity_matrix
            
        except Exception as e:
            logger.error(f"Error calculating batch similarity matrix: {e}")
            return np.array([])
    
    def normalize_embeddings(self, embeddings: List[List[float]]) -> List[List[float]]:
        """
        Normalize embeddings to unit vectors.
        
        Args:
            embeddings: List of embedding vectors
            
        Returns:
            List of normalized embedding vectors
        """
        normalized = []
        
        for embedding in embeddings:
            if not embedding:
                normalized.append([])
                continue
            
            try:
                vec = np.array(embedding, dtype=np.float64)
                norm = np.linalg.norm(vec)
                
                if norm > 0:
                    normalized_vec = vec / norm
                    normalized.append(normalized_vec.tolist())
                else:
                    normalized.append([])
                    
            except Exception as e:
                logger.error(f"Error normalizing embedding: {e}")
                normalized.append([])
        
        return normalized
    
    def calculate_embedding_statistics(self, embeddings: List[List[float]]) -> Dict[str, Any]:
        """
        Calculate statistics for a set of embeddings.
        
        Args:
            embeddings: List of embedding vectors
            
        Returns:
            Dictionary with embedding statistics
        """
        if not embeddings:
            return {
                'count': 0,
                'dimensions': 0,
                'mean_norm': 0.0,
                'std_norm': 0.0,
                'min_norm': 0.0,
                'max_norm': 0.0
            }
        
        # Filter out empty embeddings
        valid_embeddings = [emb for emb in embeddings if emb]
        
        if not valid_embeddings:
            return {
                'count': len(embeddings),
                'valid_count': 0,
                'dimensions': 0,
                'mean_norm': 0.0,
                'std_norm': 0.0,
                'min_norm': 0.0,
                'max_norm': 0.0
            }
        
        try:
            # Convert to numpy array
            embedding_matrix = np.array(valid_embeddings, dtype=np.float64)
            
            # Calculate norms
            norms = np.linalg.norm(embedding_matrix, axis=1)
            
            stats = {
                'count': len(embeddings),
                'valid_count': len(valid_embeddings),
                'dimensions': embedding_matrix.shape[1],
                'mean_norm': float(np.mean(norms)),
                'std_norm': float(np.std(norms)),
                'min_norm': float(np.min(norms)),
                'max_norm': float(np.max(norms))
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating embedding statistics: {e}")
            return {
                'count': len(embeddings),
                'valid_count': len(valid_embeddings),
                'dimensions': 0,
                'mean_norm': 0.0,
                'std_norm': 0.0,
                'min_norm': 0.0,
                'max_norm': 0.0
            } 
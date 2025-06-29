"""
OpenAI Embedding API integration for generating text embeddings.
"""

import os
import time
import logging
import json
from typing import List, Dict, Any, Optional, Union
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class OpenAIEmbedder:
    """Handles OpenAI embedding API interactions with proper error handling and rate limiting."""
    
    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        """
        Initialize OpenAI embedder.
        
        Args:
            api_key: OpenAI API key (if None, will try to get from environment)
            model: Embedding model to use
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.model = model
        self.base_url = "https://api.openai.com/v1/embeddings"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Rate limiting settings
        self.requests_per_minute = 3500  # OpenAI's limit for text-embedding-3-small
        self.requests_per_minute_large = 500  # OpenAI's limit for text-embedding-3-large
        self.max_retries = 3
        self.base_delay = 1  # Base delay in seconds
        
        # Track API usage
        self.request_count = 0
        self.last_request_time = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        
        # Cost per 1K tokens (as of 2024)
        self.cost_per_1k_tokens = {
            "text-embedding-3-small": 0.00002,  # $0.00002 per 1K tokens
            "text-embedding-3-large": 0.00013   # $0.00013 per 1K tokens
        }
        
        logger.info(f"Initialized OpenAI embedder with model: {model}")
    
    def _calculate_cost(self, tokens: int) -> float:
        """
        Calculate the cost for a given number of tokens.
        
        Args:
            tokens: Number of tokens
            
        Returns:
            Cost in USD
        """
        cost_per_1k = self.cost_per_1k_tokens.get(self.model, 0.00002)
        return (tokens / 1000) * cost_per_1k
    
    def _rate_limit_delay(self):
        """Implement rate limiting delay."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Determine rate limit based on model
        if "large" in self.model:
            min_interval = 60.0 / self.requests_per_minute_large
        else:
            min_interval = 60.0 / self.requests_per_minute
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _exponential_backoff_retry(self, func, *args, **kwargs):
        """
        Retry function with exponential backoff.
        
        Args:
            func: Function to retry
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise e
                
                delay = self.base_delay * (2 ** attempt)
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}), retrying in {delay}s: {e}")
                time.sleep(delay)
    
    def _make_api_request(self, texts: List[str]) -> Dict[str, Any]:
        """
        Make API request to OpenAI embeddings endpoint.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            API response as dictionary
        """
        payload = {
            "model": self.model,
            "input": texts,
            "encoding_format": "float"
        }
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            error_msg = f"API request failed with status {response.status_code}: {response.text}"
            logger.error(error_msg)
            raise requests.exceptions.RequestException(error_msg)
        
        return response.json()
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for a text (rough approximation).
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Rough approximation: 1 token ≈ 4 characters for English text
        return len(text) // 4
    
    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return []
        
        # Rate limiting
        self._rate_limit_delay()
        
        try:
            # Make API request with retry
            response = self._exponential_backoff_retry(self._make_api_request, [text])
            
            # Extract embedding
            embedding = response['data'][0]['embedding']
            
            # Update usage statistics
            tokens = response['usage']['total_tokens']
            self.total_tokens += tokens
            cost = self._calculate_cost(tokens)
            self.total_cost += cost
            self.request_count += 1
            
            logger.debug(f"Generated embedding for text ({len(text)} chars, ~{tokens} tokens, ${cost:.6f})")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            raise
    
    def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Embed a batch of texts efficiently.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in each batch
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        logger.info(f"Starting batch embedding of {len(texts)} texts with batch size {batch_size}")
        
        all_embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} texts)")
            
            # Rate limiting
            self._rate_limit_delay()
            
            try:
                # Make API request with retry
                response = self._exponential_backoff_retry(self._make_api_request, batch)
                
                # Extract embeddings
                batch_embeddings = [item['embedding'] for item in response['data']]
                all_embeddings.extend(batch_embeddings)
                
                # Update usage statistics
                tokens = response['usage']['total_tokens']
                self.total_tokens += tokens
                cost = self._calculate_cost(tokens)
                self.total_cost += cost
                self.request_count += 1
                
                logger.info(f"Batch {batch_num} completed: {len(batch)} texts, ~{tokens} tokens, ${cost:.6f}")
                
            except Exception as e:
                logger.error(f"Failed to embed batch {batch_num}: {e}")
                # Add empty embeddings for failed batch
                all_embeddings.extend([[] for _ in batch])
        
        logger.info(f"Batch embedding completed: {len(all_embeddings)} embeddings generated")
        return all_embeddings
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get API usage statistics.
        
        Returns:
            Dictionary with usage statistics
        """
        return {
            'request_count': self.request_count,
            'total_tokens': self.total_tokens,
            'total_cost_usd': self.total_cost,
            'model': self.model,
            'last_request_time': self.last_request_time
        }
    
    def reset_usage_stats(self):
        """Reset usage statistics."""
        self.request_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.last_request_time = 0
        logger.info("Usage statistics reset")
    
    def test_connection(self) -> bool:
        """
        Test the API connection with a simple request.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_text = "Hello, world!"
            embedding = self.embed_text(test_text)
            logger.info(f"API connection test successful. Embedding dimension: {len(embedding)}")
            return True
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False 
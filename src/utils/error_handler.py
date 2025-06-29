"""
Error handling utilities for the job scraping system.
"""

import logging
import time
from typing import Optional, Callable
from requests.exceptions import RequestException, Timeout, ConnectionError
from selenium.common.exceptions import WebDriverException, TimeoutException

logger = logging.getLogger(__name__)

class ScrapingError(Exception):
    """Base exception for scraping errors."""
    pass

class RateLimitError(ScrapingError):
    """Exception raised when rate limiting is detected."""
    pass

class RobotsTxtError(ScrapingError):
    """Exception raised when robots.txt disallows scraping."""
    pass

class DataExtractionError(ScrapingError):
    """Exception raised when data extraction fails."""
    pass

def handle_request_errors(func: Callable) -> Callable:
    """
    Decorator to handle common request errors with retry logic.
    
    Args:
        func: Function to wrap with error handling
        
    Returns:
        Wrapped function with error handling
    """
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Timeout:
                logger.warning(f"Timeout error on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise ScrapingError(f"Request timed out after {max_retries} attempts")
            except ConnectionError:
                logger.warning(f"Connection error on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise ScrapingError(f"Connection failed after {max_retries} attempts")
            except RequestException as e:
                logger.error(f"Request error: {e}")
                raise ScrapingError(f"Request failed: {e}")
        
    return wrapper

def handle_selenium_errors(func: Callable) -> Callable:
    """
    Decorator to handle common Selenium errors with retry logic.
    
    Args:
        func: Function to wrap with error handling
        
    Returns:
        Wrapped function with error handling
    """
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except TimeoutException:
                logger.warning(f"Selenium timeout on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise ScrapingError(f"Selenium operation timed out after {max_retries} attempts")
            except WebDriverException as e:
                logger.error(f"WebDriver error: {e}")
                raise ScrapingError(f"WebDriver failed: {e}")
        
    return wrapper

def check_robots_txt(url: str, user_agent: str = "*") -> bool:
    """
    Check if scraping is allowed by robots.txt.
    
    Args:
        url: Base URL to check
        user_agent: User agent string
        
    Returns:
        True if scraping is allowed, False otherwise
    """
    try:
        import requests
        from urllib.parse import urljoin, urlparse
        
        robots_url = urljoin(url, "/robots.txt")
        response = requests.get(robots_url, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"Could not fetch robots.txt from {robots_url}")
            return True  # Assume allowed if we can't check
        
        robots_content = response.text.lower()
        
        # Check for user-agent and disallow rules
        lines = robots_content.split('\n')
        current_user_agent = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('user-agent:'):
                current_user_agent = line.split(':', 1)[1].strip()
            elif line.startswith('disallow:') and (current_user_agent == user_agent or current_user_agent == '*'):
                disallow_path = line.split(':', 1)[1].strip()
                if disallow_path == '/' or disallow_path in url:
                    logger.warning(f"Scraping disallowed by robots.txt: {disallow_path}")
                    return False
        
        return True
        
    except Exception as e:
        logger.warning(f"Error checking robots.txt: {e}")
        return True  # Assume allowed if we can't check

def log_error(error: Exception, context: str = "") -> None:
    """
    Log an error with context information.
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
    """
    error_msg = f"Error in {context}: {type(error).__name__}: {str(error)}"
    logger.error(error_msg)
    
    # Log additional details for specific error types
    if isinstance(error, RequestException):
        logger.error(f"Request details: {getattr(error, 'request', 'N/A')}")
    elif isinstance(error, WebDriverException):
        logger.error(f"WebDriver details: {getattr(error, 'msg', 'N/A')}")

def safe_extract_text(element, default: str = "") -> str:
    """
    Safely extract text from a BeautifulSoup element.
    
    Args:
        element: BeautifulSoup element
        default: Default value if extraction fails
        
    Returns:
        Extracted text or default value
    """
    try:
        if element is None:
            return default
        text = element.get_text(strip=True)
        return text if text else default
    except Exception as e:
        logger.warning(f"Error extracting text: {e}")
        return default

def safe_extract_attribute(element, attribute: str, default: str = "") -> str:
    """
    Safely extract an attribute from a BeautifulSoup element.
    
    Args:
        element: BeautifulSoup element
        attribute: Attribute name to extract
        default: Default value if extraction fails
        
    Returns:
        Attribute value or default value
    """
    try:
        if element is None:
            return default
        value = element.get(attribute, default)
        return value if value else default
    except Exception as e:
        logger.warning(f"Error extracting attribute {attribute}: {e}")
        return default 
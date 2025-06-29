"""
Utility modules for the AI-Powered Job Matching System.
"""

from .data_processor import JobDataProcessor
from .error_handler import (
    ScrapingError, RateLimitError, RobotsTxtError, DataExtractionError,
    handle_request_errors, handle_selenium_errors, check_robots_txt,
    log_error, safe_extract_text, safe_extract_attribute
)

__all__ = [
    'JobDataProcessor',
    'ScrapingError', 'RateLimitError', 'RobotsTxtError', 'DataExtractionError',
    'handle_request_errors', 'handle_selenium_errors', 'check_robots_txt',
    'log_error', 'safe_extract_text', 'safe_extract_attribute'
] 
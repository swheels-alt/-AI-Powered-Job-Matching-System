"""
Configuration settings for the AI-Powered Job Matching System.
"""

from .settings import *

__all__ = [
    'INDEED_BASE_URL', 'LINKEDIN_BASE_URL', 'GLASSDOOR_BASE_URL',
    'DEFAULT_LOCATION', 'DEFAULT_KEYWORDS', 'DEFAULT_MAX_JOBS',
    'MIN_DELAY', 'MAX_DELAY', 'REQUEST_TIMEOUT', 'DEFAULT_HEADERS',
    'DATA_DIR', 'RAW_DATA_DIR', 'PROCESSED_DATA_DIR',
    'LOG_LEVEL', 'LOG_FORMAT', 'LOG_FILE', 'JOB_FIELDS'
] 
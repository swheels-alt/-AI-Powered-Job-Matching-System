"""
Configuration settings for the job scraping system.
"""

import os
from fake_useragent import UserAgent

# Base URLs for job boards
INDEED_BASE_URL = "https://www.indeed.com"
LINKEDIN_BASE_URL = "https://www.linkedin.com/jobs"
GLASSDOOR_BASE_URL = "https://www.glassdoor.com/Job"

# Default search parameters
DEFAULT_LOCATION = "St. Louis, MO"
DEFAULT_KEYWORDS = "computer science"
DEFAULT_MAX_JOBS = 100

# Rate limiting settings (in seconds)
MIN_DELAY = 2
MAX_DELAY = 5
REQUEST_TIMEOUT = 30

# User agent rotation
ua = UserAgent()
DEFAULT_HEADERS = {
    'User-Agent': ua.random,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# File paths
DATA_DIR = "data"
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

# Ensure directories exist
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "job_scraper.log"

# Data fields to extract
JOB_FIELDS = [
    'job_title',
    'company_name',
    'location',
    'job_description',
    'required_skills',
    'experience_level',
    'salary_range',
    'posted_date',
    'job_url',
    'source_website'
]

# Selenium settings
SELENIUM_IMPLICIT_WAIT = 10
SELENIUM_PAGE_LOAD_TIMEOUT = 30 
"""
Indeed job scraper with ethical considerations and error handling.
"""

import requests
import time
import random
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
from typing import List, Dict, Any, Optional

from ..config.settings import (
    INDEED_BASE_URL, MIN_DELAY, MAX_DELAY, REQUEST_TIMEOUT, DEFAULT_HEADERS
)
from ..utils.error_handler import (
    handle_request_errors, check_robots_txt, safe_extract_text, 
    safe_extract_attribute, log_error
)

logger = logging.getLogger(__name__)

class IndeedScraper:
    """Scraper for Indeed job postings with ethical considerations."""
    
    def __init__(self):
        self.base_url = INDEED_BASE_URL
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        
        # Check robots.txt before starting
        if not check_robots_txt(self.base_url):
            logger.warning("Indeed robots.txt may disallow scraping")
    
    def _rate_limit(self):
        """Implement rate limiting between requests."""
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        time.sleep(delay)
    
    @handle_request_errors
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """
        Make a request with proper error handling.
        
        Args:
            url: URL to request
            
        Returns:
            Response object or None if failed
        """
        response = self.session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response
    
    def search_jobs(self, keywords: str, location: str, max_jobs: int = 50) -> List[Dict[str, Any]]:
        """
        Search for jobs on Indeed.
        
        Args:
            keywords: Job search keywords
            location: Location to search in
            max_jobs: Maximum number of jobs to scrape
            
        Returns:
            List of job data dictionaries
        """
        jobs = []
        page = 0
        
        try:
            while len(jobs) < max_jobs:
                # Construct search URL
                search_url = self._build_search_url(keywords, location, page)
                logger.info(f"Searching Indeed page {page + 1}: {search_url}")
                
                # Make request
                response = self._make_request(search_url)
                if not response:
                    break
                
                # Parse job listings
                page_jobs = self._parse_job_listings(response.text)
                if not page_jobs:
                    logger.info("No more jobs found on this page")
                    break
                
                # Process each job
                for job_url in page_jobs:
                    if len(jobs) >= max_jobs:
                        break
                    
                    job_data = self._scrape_job_details(job_url)
                    if job_data:
                        job_data['source_website'] = 'Indeed'
                        jobs.append(job_data)
                        logger.info(f"Scraped job: {job_data.get('job_title', 'Unknown')}")
                
                page += 1
                self._rate_limit()
                
                # Safety check to prevent infinite loops
                if page > 10:
                    logger.warning("Reached maximum page limit")
                    break
            
            logger.info(f"Successfully scraped {len(jobs)} jobs from Indeed")
            return jobs
            
        except Exception as e:
            log_error(e, "Indeed search")
            return jobs
    
    def _build_search_url(self, keywords: str, location: str, page: int) -> str:
        """
        Build Indeed search URL.
        
        Args:
            keywords: Search keywords
            location: Location
            page: Page number
            
        Returns:
            Search URL
        """
        # Indeed uses a specific URL structure
        search_params = {
            'q': keywords,
            'l': location,
            'start': page * 10  # Indeed shows 10 jobs per page
        }
        
        # Build query string
        query_parts = []
        for key, value in search_params.items():
            query_parts.append(f"{key}={quote(str(value))}")
        
        return f"{self.base_url}/jobs?{'&'.join(query_parts)}"
    
    def _parse_job_listings(self, html_content: str) -> List[str]:
        """
        Parse job listing URLs from search results page.
        
        Args:
            html_content: HTML content of search results page
            
        Returns:
            List of job detail URLs
        """
        job_urls = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            # Look for job cards/containers
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            
            for card in job_cards:
                # Find job title link
                title_link = card.find('a', {'data-jk': True})
                if title_link:
                    job_id = title_link.get('data-jk')
                    if job_id:
                        job_url = f"{self.base_url}/viewjob?jk={job_id}"
                        job_urls.append(job_url)
            
            # Alternative selectors if the above doesn't work
            if not job_urls:
                job_links = soup.find_all('a', href=True)
                for link in job_links:
                    href = link.get('href', '')
                    if '/viewjob?' in href or '/rc/clk?' in href:
                        job_url = urljoin(self.base_url, href)
                        job_urls.append(job_url)
            
            logger.info(f"Found {len(job_urls)} job URLs on page")
            return job_urls
            
        except Exception as e:
            log_error(e, "parsing job listings")
            return []
    
    def _scrape_job_details(self, job_url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape detailed job information from job page.
        
        Args:
            job_url: URL of the job detail page
            
        Returns:
            Job data dictionary or None if failed
        """
        try:
            response = self._make_request(job_url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract job data
            job_data = {
                'job_url': job_url,
                'job_title': self._extract_job_title(soup),
                'company_name': self._extract_company_name(soup),
                'location': self._extract_location(soup),
                'job_description': self._extract_job_description(soup),
                'salary_range': self._extract_salary(soup),
                'posted_date': self._extract_posted_date(soup),
                'required_skills': self._extract_skills(soup),
                'experience_level': self._extract_experience_level(soup)
            }
            
            # Validate that we have essential data
            if not job_data.get('job_title') or not job_data.get('job_description'):
                logger.warning(f"Incomplete job data for {job_url}")
                return None
            
            return job_data
            
        except Exception as e:
            log_error(e, f"scraping job details from {job_url}")
            return None
    
    def _extract_job_title(self, soup: BeautifulSoup) -> str:
        """Extract job title from job page."""
        selectors = [
            'h1.jobsearch-JobInfoHeader-title',
            'h1[data-testid="jobsearch-JobInfoHeader-title"]',
            'h1',
            '.jobsearch-JobInfoHeader-title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return safe_extract_text(element)
        
        return ""
    
    def _extract_company_name(self, soup: BeautifulSoup) -> str:
        """Extract company name from job page."""
        selectors = [
            '[data-testid="jobsearch-JobInfoHeader-companyName"]',
            '.jobsearch-JobInfoHeader-companyName',
            '.companyName',
            '[data-company-name]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return safe_extract_text(element)
        
        return ""
    
    def _extract_location(self, soup: BeautifulSoup) -> str:
        """Extract job location from job page."""
        selectors = [
            '[data-testid="jobsearch-JobInfoHeader-locationText"]',
            '.jobsearch-JobInfoHeader-locationText',
            '.location',
            '[data-location]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return safe_extract_text(element)
        
        return ""
    
    def _extract_job_description(self, soup: BeautifulSoup) -> str:
        """Extract job description from job page."""
        selectors = [
            '#jobDescriptionText',
            '.jobsearch-jobDescriptionText',
            '.job-description',
            '[data-testid="jobsearch-JobComponent-description"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return safe_extract_text(element)
        
        return ""
    
    def _extract_salary(self, soup: BeautifulSoup) -> str:
        """Extract salary information from job page."""
        selectors = [
            '[data-testid="jobsearch-JobInfoHeader-salaryText"]',
            '.jobsearch-JobInfoHeader-salaryText',
            '.salary',
            '[data-salary]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return safe_extract_text(element)
        
        return ""
    
    def _extract_posted_date(self, soup: BeautifulSoup) -> str:
        """Extract posted date from job page."""
        selectors = [
            '[data-testid="jobsearch-JobInfoHeader-dateText"]',
            '.jobsearch-JobInfoHeader-dateText',
            '.date',
            '[data-date]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return safe_extract_text(element)
        
        return ""
    
    def _extract_skills(self, soup: BeautifulSoup) -> str:
        """Extract required skills from job page."""
        # Look for skills in the job description
        description = self._extract_job_description(soup)
        if description:
            # Simple keyword extraction (can be enhanced with NLP)
            skill_keywords = ['python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker']
            found_skills = []
            
            for skill in skill_keywords:
                if skill.lower() in description.lower():
                    found_skills.append(skill)
            
            return ', '.join(found_skills) if found_skills else ""
        
        return ""
    
    def _extract_experience_level(self, soup: BeautifulSoup) -> str:
        """Extract experience level from job page."""
        description = self._extract_job_description(soup)
        if description:
            description_lower = description.lower()
            
            if any(word in description_lower for word in ['senior', 'lead', 'principal']):
                return "Senior"
            elif any(word in description_lower for word in ['junior', 'entry', 'graduate']):
                return "Junior"
            elif any(word in description_lower for word in ['mid', 'intermediate']):
                return "Mid-level"
            else:
                return "Not specified"
        
        return "Not specified" 
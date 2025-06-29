"""
LinkedIn job scraper using Selenium for dynamic content.
"""

import time
import random
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from ..config.settings import (
    LINKEDIN_BASE_URL, MIN_DELAY, MAX_DELAY, SELENIUM_IMPLICIT_WAIT, 
    SELENIUM_PAGE_LOAD_TIMEOUT
)
from ..utils.error_handler import (
    handle_selenium_errors, check_robots_txt, log_error
)

logger = logging.getLogger(__name__)

class LinkedInScraper:
    """Scraper for LinkedIn job postings using Selenium."""
    
    def __init__(self, headless: bool = True):
        self.base_url = LINKEDIN_BASE_URL
        self.headless = headless
        self.driver = None
        
        # Check robots.txt before starting
        if not check_robots_txt(self.base_url):
            logger.warning("LinkedIn robots.txt may disallow scraping")
    
    def _setup_driver(self):
        """Setup Chrome WebDriver with appropriate options."""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Additional options for better performance and stealth
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
            
            # Disable images and CSS for faster loading
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Setup driver with automatic ChromeDriver management
            self.driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Set timeouts
            self.driver.implicitly_wait(SELENIUM_IMPLICIT_WAIT)
            self.driver.set_page_load_timeout(SELENIUM_PAGE_LOAD_TIMEOUT)
            
            logger.info("Chrome WebDriver setup completed")
            
        except Exception as e:
            log_error(e, "setting up Chrome WebDriver")
            raise
    
    def _rate_limit(self):
        """Implement rate limiting between requests."""
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        time.sleep(delay)
    
    @handle_selenium_errors
    def search_jobs(self, keywords: str, location: str, max_jobs: int = 30) -> List[Dict[str, Any]]:
        """
        Search for jobs on LinkedIn.
        
        Args:
            keywords: Job search keywords
            location: Location to search in
            max_jobs: Maximum number of jobs to scrape
            
        Returns:
            List of job data dictionaries
        """
        jobs = []
        
        try:
            self._setup_driver()
            
            # Build search URL
            search_url = self._build_search_url(keywords, location)
            logger.info(f"Searching LinkedIn: {search_url}")
            
            # Navigate to search page
            self.driver.get(search_url)
            self._rate_limit()
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results"))
            )
            
            # Scroll to load more jobs
            self._scroll_to_load_jobs(max_jobs)
            
            # Get job listings
            job_cards = self._get_job_cards()
            logger.info(f"Found {len(job_cards)} job cards")
            
            # Process each job
            for i, card in enumerate(job_cards[:max_jobs]):
                try:
                    job_data = self._scrape_job_from_card(card)
                    if job_data:
                        job_data['source_website'] = 'LinkedIn'
                        jobs.append(job_data)
                        logger.info(f"Scraped job {i+1}: {job_data.get('job_title', 'Unknown')}")
                    
                    self._rate_limit()
                    
                except Exception as e:
                    log_error(e, f"scraping job card {i+1}")
                    continue
            
            logger.info(f"Successfully scraped {len(jobs)} jobs from LinkedIn")
            return jobs
            
        except Exception as e:
            log_error(e, "LinkedIn search")
            return jobs
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def _build_search_url(self, keywords: str, location: str) -> str:
        """
        Build LinkedIn search URL.
        
        Args:
            keywords: Search keywords
            location: Location
            
        Returns:
            Search URL
        """
        # LinkedIn uses a specific URL structure
        search_params = {
            'keywords': keywords,
            'location': location,
            'f_TPR': 'r86400',  # Last 24 hours
            'position': 1,
            'pageNum': 0
        }
        
        # Build query string
        query_parts = []
        for key, value in search_params.items():
            query_parts.append(f"{key}={quote(str(value))}")
        
        return f"{self.base_url}/search?{'&'.join(query_parts)}"
    
    def _scroll_to_load_jobs(self, target_count: int):
        """
        Scroll down to load more job listings.
        
        Args:
            target_count: Target number of jobs to load
        """
        try:
            jobs_list = self.driver.find_element(By.CLASS_NAME, "jobs-search-results__list")
            current_count = 0
            max_scrolls = 10
            
            for scroll in range(max_scrolls):
                # Count current jobs
                job_cards = jobs_list.find_elements(By.CLASS_NAME, "job-search-card")
                current_count = len(job_cards)
                
                if current_count >= target_count:
                    break
                
                # Scroll to bottom of jobs list
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight", jobs_list
                )
                
                # Wait for new content to load
                time.sleep(2)
                
                # Check if new jobs loaded
                new_job_cards = jobs_list.find_elements(By.CLASS_NAME, "job-search-card")
                if len(new_job_cards) == current_count:
                    # No new jobs loaded, try scrolling more
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)
            
            logger.info(f"Loaded {current_count} jobs after scrolling")
            
        except Exception as e:
            log_error(e, "scrolling to load jobs")
    
    def _get_job_cards(self) -> List:
        """
        Get all job card elements from the page.
        
        Returns:
            List of job card WebElements
        """
        try:
            # Multiple possible selectors for job cards
            selectors = [
                ".job-search-card",
                ".job-card-container",
                ".job-card",
                "[data-job-id]"
            ]
            
            for selector in selectors:
                cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if cards:
                    return cards
            
            return []
            
        except Exception as e:
            log_error(e, "getting job cards")
            return []
    
    def _scrape_job_from_card(self, card) -> Optional[Dict[str, Any]]:
        """
        Scrape job data from a job card.
        
        Args:
            card: Job card WebElement
            
        Returns:
            Job data dictionary or None if failed
        """
        try:
            # Click on the job card to open details
            card.click()
            time.sleep(2)
            
            # Wait for job details to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-view-layout"))
            )
            
            # Extract job data
            job_data = {
                'job_url': self.driver.current_url,
                'job_title': self._extract_job_title(),
                'company_name': self._extract_company_name(),
                'location': self._extract_location(),
                'job_description': self._extract_job_description(),
                'salary_range': self._extract_salary(),
                'posted_date': self._extract_posted_date(),
                'required_skills': self._extract_skills(),
                'experience_level': self._extract_experience_level()
            }
            
            # Validate essential data
            if not job_data.get('job_title') or not job_data.get('job_description'):
                logger.warning(f"Incomplete job data for {job_data.get('job_url', 'Unknown URL')}")
                return None
            
            return job_data
            
        except Exception as e:
            log_error(e, "scraping job from card")
            return None
    
    def _extract_job_title(self) -> str:
        """Extract job title from job details page."""
        selectors = [
            ".job-details-jobs-unified-top-card__job-title",
            "h1",
            ".job-title",
            "[data-testid='job-title']"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                return element.text.strip()
            except NoSuchElementException:
                continue
        
        return ""
    
    def _extract_company_name(self) -> str:
        """Extract company name from job details page."""
        selectors = [
            ".job-details-jobs-unified-top-card__company-name",
            ".company-name",
            "[data-testid='company-name']"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                return element.text.strip()
            except NoSuchElementException:
                continue
        
        return ""
    
    def _extract_location(self) -> str:
        """Extract job location from job details page."""
        selectors = [
            ".job-details-jobs-unified-top-card__bullet",
            ".location",
            "[data-testid='location']"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                return element.text.strip()
            except NoSuchElementException:
                continue
        
        return ""
    
    def _extract_job_description(self) -> str:
        """Extract job description from job details page."""
        selectors = [
            ".job-description",
            ".jobs-description",
            ".job-details-jobs-unified-top-card__job-description",
            "[data-testid='job-description']"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                return element.text.strip()
            except NoSuchElementException:
                continue
        
        return ""
    
    def _extract_salary(self) -> str:
        """Extract salary information from job details page."""
        selectors = [
            ".job-details-jobs-unified-top-card__salary-info",
            ".salary",
            "[data-testid='salary']"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                return element.text.strip()
            except NoSuchElementException:
                continue
        
        return ""
    
    def _extract_posted_date(self) -> str:
        """Extract posted date from job details page."""
        selectors = [
            ".job-details-jobs-unified-top-card__posted-date",
            ".posted-date",
            "[data-testid='posted-date']"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                return element.text.strip()
            except NoSuchElementException:
                continue
        
        return ""
    
    def _extract_skills(self) -> str:
        """Extract required skills from job description."""
        description = self._extract_job_description()
        if description:
            # Simple keyword extraction
            skill_keywords = ['python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker']
            found_skills = []
            
            for skill in skill_keywords:
                if skill.lower() in description.lower():
                    found_skills.append(skill)
            
            return ', '.join(found_skills) if found_skills else ""
        
        return ""
    
    def _extract_experience_level(self) -> str:
        """Extract experience level from job description."""
        description = self._extract_job_description()
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
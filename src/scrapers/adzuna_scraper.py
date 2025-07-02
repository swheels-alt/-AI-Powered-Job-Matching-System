"""
Adzuna API scraper for job postings.
Free API with good St. Louis coverage.
"""

import requests
import time
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)

class AdzunaScraper:
    """Scraper for Adzuna job postings using their free API."""
    
    def __init__(self, app_id: str = None, app_key: str = None):
        """
        Initialize Adzuna scraper.
        
        Args:
            app_id: Adzuna app ID (get from https://developer.adzuna.com/)
            app_key: Adzuna app key
        """
        self.base_url = "https://api.adzuna.com/v1/api/jobs/us/search"
        self.app_id = app_id or "demo"  # Use demo if no credentials provided
        self.app_key = app_key or "demo"
        
        if app_id == "demo" or app_key == "demo":
            logger.warning("Using demo credentials. Sign up at https://developer.adzuna.com/ for full access")
    
    def search_jobs(self, keywords: str, location: str = "St. Louis, MO", max_jobs: int = 50) -> List[Dict[str, Any]]:
        """
        Search for jobs using Adzuna API.
        
        Args:
            keywords: Job search keywords
            location: Location to search in
            max_jobs: Maximum number of jobs to return
            
        Returns:
            List of job data dictionaries
        """
        jobs = []
        page = 1
        
        try:
            while len(jobs) < max_jobs:
                # Build API request
                params = {
                    'app_id': self.app_id,
                    'app_key': self.app_key,
                    'results_per_page': min(50, max_jobs - len(jobs)),  # Max 50 per page
                    'what': keywords,
                    'where': location,
                    'page': page
                }
                
                logger.info(f"Searching Adzuna page {page} for '{keywords}' in '{location}'")
                
                # Make API request
                response = requests.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # Extract jobs from response
                page_jobs = data.get('results', [])
                if not page_jobs:
                    logger.info("No more jobs found")
                    break
                
                # Process each job
                for job_data in page_jobs:
                    if len(jobs) >= max_jobs:
                        break
                    
                    processed_job = self._process_job_data(job_data)
                    if processed_job:
                        jobs.append(processed_job)
                
                page += 1
                
                # Rate limiting
                time.sleep(1)
                
                # Safety check
                if page > 10:
                    logger.warning("Reached maximum page limit")
                    break
            
            logger.info(f"Successfully retrieved {len(jobs)} jobs from Adzuna")
            return jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {e}")
            return jobs
        except Exception as e:
            logger.error(f"Error searching Adzuna: {e}")
            return jobs
    
    def _process_job_data(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process raw job data from Adzuna API.
        
        Args:
            job_data: Raw job data from API
            
        Returns:
            Processed job data dictionary
        """
        try:
            # Extract location information
            location_data = job_data.get('location', {})
            location_display = location_data.get('display_name', '')
            
            # Extract company information
            company_data = job_data.get('company', {})
            company_name = company_data.get('display_name', '')
            
            # Extract salary information
            salary_data = job_data.get('salary_min', 0)
            salary_max = job_data.get('salary_max', 0)
            salary_currency = job_data.get('salary_currency', 'USD')
            
            # Format salary
            if salary_data and salary_max:
                salary_range = f"{salary_currency} {salary_data:,} - {salary_max:,}"
            elif salary_data:
                salary_range = f"{salary_currency} {salary_data:,}+"
            else:
                salary_range = "Not specified"
            
            # Extract description
            description = job_data.get('description', '')
            if description:
                # Clean HTML tags if present
                import re
                description = re.sub(r'<[^>]+>', '', description)
                description = description.replace('&nbsp;', ' ').strip()
            
            # Extract skills from description
            skills = self._extract_skills_from_description(description)
            
            # Determine experience level
            experience_level = self._determine_experience_level(description, job_data.get('title', ''))
            
            processed_job = {
                'job_title': job_data.get('title', ''),
                'company_name': company_name,
                'location': location_display,
                'job_description': description,
                'required_skills': ', '.join(skills),
                'experience_level': experience_level,
                'salary_range': salary_range,
                'posted_date': job_data.get('created', ''),
                'job_url': job_data.get('redirect_url', ''),
                'source_website': 'Adzuna',
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return processed_job
            
        except Exception as e:
            logger.error(f"Error processing job data: {e}")
            return None
    
    def _extract_skills_from_description(self, description: str) -> List[str]:
        """
        Extract skills from job description.
        
        Args:
            description: Job description text
            
        Returns:
            List of extracted skills
        """
        # Common tech skills to look for
        tech_skills = [
            'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring',
            'sql', 'mongodb', 'postgresql', 'mysql', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
            'git', 'github', 'gitlab', 'jira', 'agile', 'scrum',
            'machine learning', 'ai', 'data science', 'analytics',
            'html', 'css', 'bootstrap', 'tailwind', 'sass', 'less'
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in tech_skills:
            if skill in description_lower:
                found_skills.append(skill)
        
        return found_skills[:10]  # Limit to top 10 skills
    
    def _determine_experience_level(self, description: str, title: str) -> str:
        """
        Determine experience level from job title and description.
        
        Args:
            description: Job description
            title: Job title
            
        Returns:
            Experience level string
        """
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ['senior', 'lead', 'principal', 'architect', 'manager']):
            return 'senior'
        elif any(word in text for word in ['junior', 'entry', 'graduate', 'intern']):
            return 'junior'
        elif any(word in text for word in ['mid', 'intermediate', 'experienced']):
            return 'mid-level'
        else:
            return 'not specified'
    
    def get_job_categories(self) -> List[Dict[str, Any]]:
        """
        Get available job categories from Adzuna.
        
        Returns:
            List of job categories
        """
        try:
            url = "https://api.adzuna.com/v1/api/jobs/us/categories"
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('results', [])
            
        except Exception as e:
            logger.error(f"Error getting job categories: {e}")
            return []
    
    def get_salary_ranges(self, location: str = "St. Louis, MO") -> Dict[str, Any]:
        """
        Get salary range information for a location.
        
        Args:
            location: Location to get salary data for
            
        Returns:
            Salary range data
        """
        try:
            url = "https://api.adzuna.com/v1/api/jobs/us/salary_ranges"
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'location0': location
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('results', {})
            
        except Exception as e:
            logger.error(f"Error getting salary ranges: {e}")
            return {} 
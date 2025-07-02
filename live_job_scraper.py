#!/usr/bin/env python3
"""
Live Job Scraper for St. Louis Area
Actually scrapes real job data from Indeed and LinkedIn.
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.indeed_scraper import IndeedScraper
from scrapers.linkedin_scraper import LinkedInScraper
from utils.data_processor import JobDataProcessor
from config.settings import DEFAULT_LOCATION, RAW_DATA_DIR

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class LiveJobScraper:
    """Live job scraper for St. Louis area."""
    
    def __init__(self):
        self.indeed_scraper = IndeedScraper()
        self.linkedin_scraper = LinkedInScraper(headless=True)
        self.data_processor = JobDataProcessor()
        
    def scrape_st_louis_jobs(self, keywords: str = "software engineer", max_jobs_per_source: int = 25) -> Dict[str, Any]:
        """
        Scrape jobs from St. Louis area.
        
        Args:
            keywords: Job search keywords
            max_jobs_per_source: Maximum jobs per source
            
        Returns:
            Dictionary with scraped jobs and statistics
        """
        logger.info(f"Starting live job scraping for St. Louis area")
        logger.info(f"Keywords: {keywords}")
        logger.info(f"Max jobs per source: {max_jobs_per_source}")
        
        all_jobs = []
        statistics = {
            'total_jobs': 0,
            'indeed_jobs': 0,
            'linkedin_jobs': 0,
            'unique_companies': set(),
            'unique_locations': set(),
            'scraping_errors': 0,
            'start_time': datetime.now().isoformat(),
            'end_time': None
        }
        
        # Scrape from Indeed
        logger.info("Scraping from Indeed...")
        try:
            indeed_jobs = self.indeed_scraper.search_jobs(
                keywords=keywords,
                location=DEFAULT_LOCATION,
                max_jobs=max_jobs_per_source
            )
            statistics['indeed_jobs'] = len(indeed_jobs)
            all_jobs.extend(indeed_jobs)
            logger.info(f"Scraped {len(indeed_jobs)} jobs from Indeed")
        except Exception as e:
            logger.error(f"Error scraping from Indeed: {e}")
            statistics['scraping_errors'] += 1
        
        # Scrape from LinkedIn
        logger.info("Scraping from LinkedIn...")
        try:
            linkedin_jobs = self.linkedin_scraper.search_jobs(
                keywords=keywords,
                location=DEFAULT_LOCATION,
                max_jobs=max_jobs_per_source
            )
            statistics['linkedin_jobs'] = len(linkedin_jobs)
            all_jobs.extend(linkedin_jobs)
            logger.info(f"Scraped {len(linkedin_jobs)} jobs from LinkedIn")
        except Exception as e:
            logger.error(f"Error scraping from LinkedIn: {e}")
            statistics['scraping_errors'] += 1
        
        # Process and clean jobs
        logger.info("Processing and cleaning scraped jobs...")
        cleaned_jobs = self.data_processor.clean_job_data(all_jobs)
        
        # Remove duplicates
        unique_jobs = self.data_processor.remove_duplicates(cleaned_jobs)
        
        # Calculate statistics
        statistics['total_jobs'] = len(unique_jobs)
        statistics['unique_companies'] = len(set(job.get('company_name', '') for job in unique_jobs if job.get('company_name')))
        statistics['unique_locations'] = len(set(job.get('location', '') for job in unique_jobs if job.get('location')))
        statistics['end_time'] = datetime.now().isoformat()
        
        # Add metadata
        for job in unique_jobs:
            job['scraped_at'] = datetime.now().isoformat()
        
        return {
            'jobs': unique_jobs,
            'statistics': statistics
        }
    
    def save_results(self, results: Dict[str, Any], keywords: str) -> str:
        """
        Save scraped results to files.
        
        Args:
            results: Scraped results
            keywords: Search keywords used
            
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"st_louis_{keywords.replace(' ', '_')}_{timestamp}"
        
        # Save as JSON
        json_path = os.path.join(RAW_DATA_DIR, f"{filename}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save as CSV
        csv_path = os.path.join(RAW_DATA_DIR, f"{filename}.csv")
        self.data_processor.save_to_csv(results['jobs'], csv_path)
        
        logger.info(f"Results saved to:")
        logger.info(f"  JSON: {json_path}")
        logger.info(f"  CSV: {csv_path}")
        
        return json_path

def main():
    """Main function to run live job scraping."""
    print("🚀 Live Job Scraper for St. Louis Area")
    print("=" * 50)
    
    # Initialize scraper
    scraper = LiveJobScraper()
    
    # Define search keywords for St. Louis tech jobs
    search_keywords = [
        "software engineer",
        "python developer", 
        "data scientist",
        "web developer",
        "devops engineer",
        "frontend developer",
        "backend developer",
        "full stack developer"
    ]
    
    all_results = []
    
    for keywords in search_keywords:
        print(f"\n🔍 Searching for: {keywords}")
        print("-" * 30)
        
        try:
            # Scrape jobs
            results = scraper.scrape_st_louis_jobs(
                keywords=keywords,
                max_jobs_per_source=15  # Conservative limit
            )
            
            # Save results
            file_path = scraper.save_results(results, keywords)
            all_results.append(results)
            
            # Print summary
            stats = results['statistics']
            print(f"✅ Found {stats['total_jobs']} jobs")
            print(f"   Indeed: {stats['indeed_jobs']}")
            print(f"   LinkedIn: {stats['linkedin_jobs']}")
            print(f"   Companies: {stats['unique_companies']}")
            print(f"   Locations: {stats['unique_locations']}")
            
        except Exception as e:
            logger.error(f"Error scraping {keywords}: {e}")
            print(f"❌ Error scraping {keywords}: {e}")
            continue
    
    # Create combined results
    if all_results:
        combined_jobs = []
        total_stats = {
            'total_jobs': 0,
            'indeed_jobs': 0,
            'linkedin_jobs': 0,
            'unique_companies': set(),
            'unique_locations': set(),
            'search_terms': search_keywords,
            'scraping_errors': 0
        }
        
        for result in all_results:
            combined_jobs.extend(result['jobs'])
            stats = result['statistics']
            total_stats['indeed_jobs'] += stats['indeed_jobs']
            total_stats['linkedin_jobs'] += stats['linkedin_jobs']
            total_stats['scraping_errors'] += stats['scraping_errors']
        
        # Remove duplicates from combined results
        data_processor = JobDataProcessor()
        unique_combined_jobs = data_processor.remove_duplicates(combined_jobs)
        
        total_stats['total_jobs'] = len(unique_combined_jobs)
        total_stats['unique_companies'] = len(set(job.get('company_name', '') for job in unique_combined_jobs if job.get('company_name')))
        total_stats['unique_locations'] = len(set(job.get('location', '') for job in unique_combined_jobs if job.get('location')))
        
        # Save combined results
        combined_results = {
            'jobs': unique_combined_jobs,
            'statistics': total_stats
        }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        combined_filename = f"st_louis_combined_{timestamp}"
        combined_path = scraper.save_results(combined_results, combined_filename)
        
        print(f"\n🎯 Combined Results:")
        print(f"   Total unique jobs: {total_stats['total_jobs']}")
        print(f"   Total companies: {total_stats['unique_companies']}")
        print(f"   Total locations: {total_stats['unique_locations']}")
        print(f"   Search terms: {', '.join(search_keywords)}")
        print(f"   Saved to: {combined_path}")
    
    print(f"\n✅ Live scraping completed!")
    print(f"📁 Check the 'data/raw/' directory for results")
    print(f"📋 Check 'live_scraper.log' for detailed logs")

if __name__ == "__main__":
    main() 
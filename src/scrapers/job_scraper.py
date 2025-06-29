"""
Main job scraper that orchestrates scraping from multiple job boards.
"""

import argparse
import logging
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.settings import (
    DEFAULT_LOCATION, DEFAULT_KEYWORDS, DEFAULT_MAX_JOBS,
    LOG_LEVEL, LOG_FORMAT, LOG_FILE
)
from utils.data_processor import JobDataProcessor
from utils.error_handler import log_error
from indeed_scraper import IndeedScraper
from linkedin_scraper import LinkedInScraper

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class JobScraper:
    """Main job scraper that coordinates scraping from multiple sources."""
    
    def __init__(self):
        self.data_processor = JobDataProcessor()
        self.scrapers = {
            'indeed': IndeedScraper(),
            'linkedin': LinkedInScraper(headless=True)
        }
    
    def scrape_all_sources(self, keywords: str, location: str, max_jobs: int = 50) -> List[Dict[str, Any]]:
        """
        Scrape jobs from all available sources.
        
        Args:
            keywords: Job search keywords
            location: Location to search in
            max_jobs: Maximum number of jobs per source
            
        Returns:
            List of all scraped job data
        """
        all_jobs = []
        
        logger.info(f"Starting job scraping for '{keywords}' in '{location}'")
        logger.info(f"Target: {max_jobs} jobs per source")
        
        # Scrape from each source
        for source_name, scraper in self.scrapers.items():
            try:
                logger.info(f"Scraping from {source_name.upper()}...")
                
                jobs = scraper.search_jobs(
                    keywords=keywords,
                    location=location,
                    max_jobs=max_jobs
                )
                
                if jobs:
                    # Clean and validate jobs
                    cleaned_jobs = []
                    for job in jobs:
                        cleaned_job = self.data_processor.clean_job_data(job)
                        if self.data_processor.validate_job_data(cleaned_job):
                            cleaned_jobs.append(cleaned_job)
                    
                    all_jobs.extend(cleaned_jobs)
                    logger.info(f"Successfully scraped {len(cleaned_jobs)} valid jobs from {source_name}")
                else:
                    logger.warning(f"No jobs found from {source_name}")
                
            except Exception as e:
                log_error(e, f"scraping from {source_name}")
                continue
        
        # Remove duplicates and generate summary
        unique_jobs = self.data_processor.merge_job_data([all_jobs])
        stats = self.data_processor.generate_summary_stats(unique_jobs)
        
        logger.info(f"Scraping completed. Total unique jobs: {len(unique_jobs)}")
        logger.info(f"Summary: {stats}")
        
        return unique_jobs
    
    def save_results(self, jobs: List[Dict[str, Any]], base_filename: str = None) -> Dict[str, str]:
        """
        Save scraped jobs to both CSV and JSON formats.
        
        Args:
            jobs: List of job data dictionaries
            base_filename: Base filename for output files
            
        Returns:
            Dictionary with paths to saved files
        """
        if not base_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"jobs_{timestamp}"
        
        saved_files = {}
        
        try:
            # Save to CSV
            csv_filename = f"{base_filename}.csv"
            csv_path = self.data_processor.save_to_csv(jobs, csv_filename)
            saved_files['csv'] = csv_path
            
            # Save to JSON
            json_filename = f"{base_filename}.json"
            json_path = self.data_processor.save_to_json(jobs, json_filename)
            saved_files['json'] = json_path
            
            logger.info(f"Results saved to: {list(saved_files.values())}")
            
        except Exception as e:
            log_error(e, "saving results")
        
        return saved_files
    
    def filter_and_save(self, jobs: List[Dict[str, Any]], 
                       location: Optional[str] = None,
                       keywords: Optional[List[str]] = None,
                       company: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Filter jobs based on criteria and save filtered results.
        
        Args:
            jobs: List of job data dictionaries
            location: Location filter
            keywords: Keywords filter
            company: Company filter
            
        Returns:
            Filtered job data
        """
        filtered_jobs = self.data_processor.filter_jobs(
            jobs, location=location, keywords=keywords, company=company
        )
        
        if filtered_jobs:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filter_suffix = "_filtered"
            
            # Create descriptive filename
            filename_parts = [f"jobs{filter_suffix}"]
            if location:
                filename_parts.append(f"loc_{location.replace(' ', '_')}")
            if keywords:
                filename_parts.append(f"kw_{'_'.join(keywords)}")
            if company:
                filename_parts.append(f"comp_{company.replace(' ', '_')}")
            
            filename_parts.append(timestamp)
            base_filename = "_".join(filename_parts)
            
            self.save_results(filtered_jobs, base_filename)
        
        return filtered_jobs

def main():
    """Main function to run the job scraper from command line."""
    parser = argparse.ArgumentParser(description='Scrape job postings from multiple sources')
    
    parser.add_argument(
        '--keywords', '-k',
        type=str,
        default=DEFAULT_KEYWORDS,
        help=f'Job search keywords (default: {DEFAULT_KEYWORDS})'
    )
    
    parser.add_argument(
        '--location', '-l',
        type=str,
        default=DEFAULT_LOCATION,
        help=f'Location to search in (default: {DEFAULT_LOCATION})'
    )
    
    parser.add_argument(
        '--max-jobs', '-m',
        type=int,
        default=DEFAULT_MAX_JOBS,
        help=f'Maximum number of jobs per source (default: {DEFAULT_MAX_JOBS})'
    )
    
    parser.add_argument(
        '--sources',
        nargs='+',
        choices=['indeed', 'linkedin'],
        default=['indeed', 'linkedin'],
        help='Job sources to scrape from (default: all)'
    )
    
    parser.add_argument(
        '--filter-location',
        type=str,
        help='Filter results by location'
    )
    
    parser.add_argument(
        '--filter-keywords',
        nargs='+',
        help='Filter results by keywords'
    )
    
    parser.add_argument(
        '--filter-company',
        type=str,
        help='Filter results by company'
    )
    
    parser.add_argument(
        '--output-prefix',
        type=str,
        help='Custom prefix for output filenames'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize scraper
        scraper = JobScraper()
        
        # Filter scrapers based on user selection
        selected_scrapers = {k: v for k, v in scraper.scrapers.items() if k in args.sources}
        scraper.scrapers = selected_scrapers
        
        logger.info(f"Using sources: {list(selected_scrapers.keys())}")
        
        # Scrape jobs
        jobs = scraper.scrape_all_sources(
            keywords=args.keywords,
            location=args.location,
            max_jobs=args.max_jobs
        )
        
        if not jobs:
            logger.warning("No jobs were scraped successfully")
            return
        
        # Save all results
        base_filename = args.output_prefix if args.output_prefix else None
        saved_files = scraper.save_results(jobs, base_filename)
        
        # Apply filters if specified
        if any([args.filter_location, args.filter_keywords, args.filter_company]):
            logger.info("Applying filters to results...")
            filtered_jobs = scraper.filter_and_save(
                jobs,
                location=args.filter_location,
                keywords=args.filter_keywords,
                company=args.filter_company
            )
            
            if filtered_jobs:
                logger.info(f"Filtered results: {len(filtered_jobs)} jobs")
            else:
                logger.warning("No jobs match the specified filters")
        
        logger.info("Job scraping completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        log_error(e, "main execution")
        sys.exit(1)

if __name__ == "__main__":
    main() 
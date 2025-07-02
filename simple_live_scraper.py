#!/usr/bin/env python3
"""
Simple Live Job Scraper for St. Louis Area
Scrapes real job data from Indeed and LinkedIn for testing.
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.scrapers.indeed_scraper import IndeedScraper
from src.scrapers.linkedin_scraper import LinkedInScraper
from src.utils.data_processor import JobDataProcessor
from src.config.settings import DEFAULT_LOCATION, RAW_DATA_DIR

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_live_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def scrape_single_search(keywords: str = "software engineer", max_jobs: int = 10):
    """
    Scrape jobs for a single search term.
    
    Args:
        keywords: Job search keywords
        max_jobs: Maximum jobs to scrape per source
    """
    print(f"🔍 Scraping jobs for: '{keywords}' in {DEFAULT_LOCATION}")
    print("=" * 60)
    
    all_jobs = []
    
    # Scrape from Indeed
    print("\n📋 Scraping from Indeed...")
    try:
        indeed_scraper = IndeedScraper()
        indeed_jobs = indeed_scraper.search_jobs(
            keywords=keywords,
            location=DEFAULT_LOCATION,
            max_jobs=max_jobs
        )
        print(f"✅ Found {len(indeed_jobs)} jobs on Indeed")
        all_jobs.extend(indeed_jobs)
        
        # Show sample jobs
        for i, job in enumerate(indeed_jobs[:3]):
            print(f"   {i+1}. {job.get('job_title', 'N/A')} at {job.get('company_name', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Error scraping from Indeed: {e}")
        logger.error(f"Indeed scraping error: {e}")
    
    # Scrape from LinkedIn
    print("\n💼 Scraping from LinkedIn...")
    try:
        linkedin_scraper = LinkedInScraper(headless=True)
        linkedin_jobs = linkedin_scraper.search_jobs(
            keywords=keywords,
            location=DEFAULT_LOCATION,
            max_jobs=max_jobs
        )
        print(f"✅ Found {len(linkedin_jobs)} jobs on LinkedIn")
        all_jobs.extend(linkedin_jobs)
        
        # Show sample jobs
        for i, job in enumerate(linkedin_jobs[:3]):
            print(f"   {i+1}. {job.get('job_title', 'N/A')} at {job.get('company_name', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Error scraping from LinkedIn: {e}")
        logger.error(f"LinkedIn scraping error: {e}")
    
    # Process and save results
    if all_jobs:
        print(f"\n📊 Processing {len(all_jobs)} total jobs...")
        
        # Clean and deduplicate
        data_processor = JobDataProcessor()
        cleaned_jobs = data_processor.clean_job_data(all_jobs)
        unique_jobs = data_processor.remove_duplicates(cleaned_jobs)
        
        print(f"✅ After cleaning: {len(unique_jobs)} unique jobs")
        
        # Add metadata
        for job in unique_jobs:
            job['scraped_at'] = datetime.now().isoformat()
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"st_louis_{keywords.replace(' ', '_')}_{timestamp}"
        
        # Save JSON
        json_path = os.path.join(RAW_DATA_DIR, f"{filename}.json")
        results = {
            'jobs': unique_jobs,
            'statistics': {
                'total_jobs': len(unique_jobs),
                'indeed_jobs': len([j for j in all_jobs if j.get('source_website') == 'Indeed']),
                'linkedin_jobs': len([j for j in all_jobs if j.get('source_website') == 'LinkedIn']),
                'unique_companies': len(set(j.get('company_name', '') for j in unique_jobs if j.get('company_name'))),
                'search_keywords': keywords,
                'location': DEFAULT_LOCATION,
                'scraped_at': datetime.now().isoformat()
            }
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save CSV
        csv_path = os.path.join(RAW_DATA_DIR, f"{filename}.csv")
        data_processor.save_to_csv(unique_jobs, csv_path)
        
        print(f"\n💾 Results saved:")
        print(f"   JSON: {json_path}")
        print(f"   CSV: {csv_path}")
        
        # Show summary
        stats = results['statistics']
        print(f"\n📈 Summary:")
        print(f"   Total jobs: {stats['total_jobs']}")
        print(f"   Indeed jobs: {stats['indeed_jobs']}")
        print(f"   LinkedIn jobs: {stats['linkedin_jobs']}")
        print(f"   Unique companies: {stats['unique_companies']}")
        
        return results
    else:
        print("❌ No jobs found")
        return None

def main():
    """Main function."""
    print("🚀 Simple Live Job Scraper for St. Louis")
    print("=" * 60)
    
    # Test with a single search term
    keywords = "python developer"
    max_jobs = 10
    
    print(f"Searching for: '{keywords}'")
    print(f"Max jobs per source: {max_jobs}")
    print(f"Location: {DEFAULT_LOCATION}")
    
    results = scrape_single_search(keywords, max_jobs)
    
    if results:
        print(f"\n✅ Scraping completed successfully!")
        print(f"📁 Check 'data/raw/' for results")
        print(f"📋 Check 'simple_live_scraper.log' for details")
    else:
        print(f"\n❌ Scraping failed or no results found")
        print(f"📋 Check 'simple_live_scraper.log' for error details")

if __name__ == "__main__":
    main() 
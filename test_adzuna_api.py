#!/usr/bin/env python3
"""
Test script for Adzuna API - Free job data for St. Louis
"""

import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.adzuna_scraper import AdzunaScraper
from utils.data_processor import JobDataProcessor

def test_adzuna_api():
    """Test the Adzuna API with demo credentials."""
    print("🚀 Testing Adzuna API for St. Louis Jobs")
    print("=" * 50)
    
    # Initialize scraper with demo credentials
    scraper = AdzunaScraper()
    
    # Test search terms for St. Louis
    search_terms = [
        "software engineer",
        "python developer",
        "data scientist",
        "web developer"
    ]
    
    all_jobs = []
    
    for term in search_terms:
        print(f"\n🔍 Searching for: '{term}' in St. Louis, MO")
        print("-" * 40)
        
        try:
            # Search for jobs
            jobs = scraper.search_jobs(
                keywords=term,
                location="St. Louis, MO",
                max_jobs=10
            )
            
            print(f"✅ Found {len(jobs)} jobs for '{term}'")
            
            # Show sample jobs
            for i, job in enumerate(jobs[:3]):
                print(f"   {i+1}. {job.get('job_title', 'N/A')} at {job.get('company_name', 'N/A')}")
                print(f"      Location: {job.get('location', 'N/A')}")
                print(f"      Salary: {job.get('salary_range', 'N/A')}")
                print(f"      Skills: {job.get('required_skills', 'N/A')[:50]}...")
                print()
            
            all_jobs.extend(jobs)
            
        except Exception as e:
            print(f"❌ Error searching for '{term}': {e}")
            continue
    
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
        filename = f"st_louis_adzuna_{timestamp}"
        
        # Save JSON
        json_path = os.path.join("data/raw", f"{filename}.json")
        results = {
            'jobs': unique_jobs,
            'statistics': {
                'total_jobs': len(unique_jobs),
                'unique_companies': len(set(j.get('company_name', '') for j in unique_jobs if j.get('company_name'))),
                'search_terms': search_terms,
                'location': 'St. Louis, MO',
                'source': 'Adzuna API',
                'scraped_at': datetime.now().isoformat()
            }
        }
        
        # Ensure directory exists
        os.makedirs("data/raw", exist_ok=True)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save CSV
        csv_path = os.path.join("data/raw", f"{filename}.csv")
        data_processor.save_to_csv(unique_jobs, csv_path)
        
        print(f"\n💾 Results saved:")
        print(f"   JSON: {json_path}")
        print(f"   CSV: {csv_path}")
        
        # Show summary
        stats = results['statistics']
        print(f"\n📈 Summary:")
        print(f"   Total jobs: {stats['total_jobs']}")
        print(f"   Unique companies: {stats['unique_companies']}")
        print(f"   Search terms: {', '.join(search_terms)}")
        
        # Show some sample job titles
        print(f"\n📋 Sample Job Titles:")
        for i, job in enumerate(unique_jobs[:5]):
            print(f"   {i+1}. {job.get('job_title', 'N/A')}")
        
        return results
    else:
        print("❌ No jobs found")
        return None

def test_api_features():
    """Test additional API features."""
    print(f"\n🔧 Testing Additional API Features")
    print("=" * 50)
    
    scraper = AdzunaScraper()
    
    # Test job categories
    print("\n📂 Getting job categories...")
    try:
        categories = scraper.get_job_categories()
        print(f"✅ Found {len(categories)} job categories")
        for i, cat in enumerate(categories[:5]):
            print(f"   {i+1}. {cat.get('label', 'N/A')}")
    except Exception as e:
        print(f"❌ Error getting categories: {e}")
    
    # Test salary ranges
    print("\n💰 Getting salary ranges for St. Louis...")
    try:
        salary_data = scraper.get_salary_ranges("St. Louis, MO")
        print(f"✅ Retrieved salary data")
        if salary_data:
            print(f"   Data keys: {list(salary_data.keys())}")
    except Exception as e:
        print(f"❌ Error getting salary data: {e}")

def main():
    """Main function."""
    print("🎯 Adzuna API Test for St. Louis Job Data")
    print("=" * 60)
    print("This will test the free Adzuna API to get real job data")
    print("from St. Louis area using demo credentials.")
    print()
    
    # Test basic functionality
    results = test_adzuna_api()
    
    # Test additional features
    test_api_features()
    
    if results:
        print(f"\n✅ API test completed successfully!")
        print(f"📁 Check 'data/raw/' for results")
        print(f"🔗 Sign up at https://developer.adzuna.com/ for full access")
    else:
        print(f"\n❌ API test failed")
        print(f"🔗 Try signing up at https://developer.adzuna.com/ for better access")

if __name__ == "__main__":
    main() 
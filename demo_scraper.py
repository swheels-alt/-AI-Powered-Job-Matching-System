#!/usr/bin/env python3
"""
Demonstration script for the job scraper system.
This script shows how to use the actual scraper with different configurations.
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def demonstrate_scraper_usage():
    """Demonstrate how to use the job scraper."""
    print("🔧 Job Scraper Usage Examples")
    print("=" * 50)
    
    print("\n1. Basic Usage (Default settings):")
    print("   python src/scrapers/job_scraper.py")
    print("   # Searches for 'computer science' jobs in 'St. Louis, MO'")
    
    print("\n2. Custom Keywords and Location:")
    print("   python src/scrapers/job_scraper.py --keywords 'python developer' --location 'New York, NY'")
    
    print("\n3. Limit Number of Jobs:")
    print("   python src/scrapers/job_scraper.py --max-jobs 25")
    
    print("\n4. Use Specific Sources:")
    print("   python src/scrapers/job_scraper.py --sources indeed")
    print("   python src/scrapers/job_scraper.py --sources linkedin")
    
    print("\n5. Filter Results:")
    print("   python src/scrapers/job_scraper.py --filter-location 'Remote'")
    print("   python src/scrapers/job_scraper.py --filter-keywords python javascript")
    print("   python src/scrapers/job_scraper.py --filter-company 'Google'")
    
    print("\n6. Custom Output Filename:")
    print("   python src/scrapers/job_scraper.py --output-prefix 'tech_jobs'")
    
    print("\n7. Complete Example:")
    print("   python src/scrapers/job_scraper.py \\")
    print("     --keywords 'software engineer' \\")
    print("     --location 'San Francisco, CA' \\")
    print("     --max-jobs 50 \\")
    print("     --sources indeed linkedin \\")
    print("     --filter-keywords python react \\")
    print("     --output-prefix 'sf_software_jobs'")

def show_configuration_options():
    """Show available configuration options."""
    print("\n⚙️  Configuration Options")
    print("=" * 50)
    
    print("\n📁 Data Storage:")
    print("   - Raw data: data/raw/")
    print("   - Processed data: data/processed/")
    print("   - Logs: job_scraper.log")
    
    print("\n🔧 Settings (src/config/settings.py):")
    print("   - DEFAULT_LOCATION: 'St. Louis, MO'")
    print("   - DEFAULT_KEYWORDS: 'computer science'")
    print("   - DEFAULT_MAX_JOBS: 100")
    print("   - MIN_DELAY: 2 seconds")
    print("   - MAX_DELAY: 5 seconds")
    
    print("\n📊 Output Formats:")
    print("   - CSV: Structured data for analysis")
    print("   - JSON: Complete data with metadata")
    
    print("\n🛡️  Ethical Features:")
    print("   - robots.txt compliance checking")
    print("   - Rate limiting between requests")
    print("   - User-agent rotation")
    print("   - Error handling and retry logic")

def show_data_fields():
    """Show the data fields that are extracted."""
    print("\n📋 Extracted Data Fields")
    print("=" * 50)
    
    fields = [
        "job_title",
        "company_name", 
        "location",
        "job_description",
        "required_skills",
        "experience_level",
        "salary_range",
        "posted_date",
        "job_url",
        "source_website",
        "scraped_at"
    ]
    
    for i, field in enumerate(fields, 1):
        print(f"   {i:2d}. {field}")

def show_error_handling():
    """Show error handling capabilities."""
    print("\n🚨 Error Handling Features")
    print("=" * 50)
    
    print("✅ Network Errors:")
    print("   - Connection timeouts")
    print("   - DNS resolution failures")
    print("   - HTTP error responses")
    
    print("\n✅ Scraping Errors:")
    print("   - Missing HTML elements")
    print("   - Changed website structure")
    print("   - Rate limiting detection")
    
    print("\n✅ Data Validation:")
    print("   - Required field checking")
    print("   - Data quality validation")
    print("   - Duplicate detection")
    
    print("\n✅ Recovery Mechanisms:")
    print("   - Automatic retry logic")
    print("   - Fallback selectors")
    print("   - Graceful degradation")

def main():
    """Main demonstration function."""
    print("🚀 AI-Powered Job Matching System - Stage 1")
    print("Job Scraper Demonstration")
    print("=" * 60)
    
    demonstrate_scraper_usage()
    show_configuration_options()
    show_data_fields()
    show_error_handling()
    
    print("\n" + "=" * 60)
    print("🎯 Ready for Production Use!")
    print("\nThe system includes:")
    print("✅ Comprehensive error handling")
    print("✅ Ethical scraping practices")
    print("✅ Multiple data sources")
    print("✅ Data validation and cleaning")
    print("✅ Flexible configuration options")
    print("✅ Multiple output formats")
    
    print(f"\n📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔗 Repository: https://github.com/swheels-alt/-AI-Powered-Job-Matching-System.git")

if __name__ == "__main__":
    main() 
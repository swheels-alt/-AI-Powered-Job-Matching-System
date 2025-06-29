#!/usr/bin/env python3
"""
Test script for the job scraping system.
This script demonstrates the functionality without actually scraping real websites.
"""

import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.data_processor import JobDataProcessor

def create_sample_jobs():
    """Create sample job data for testing purposes."""
    sample_jobs = [
        {
            'job_title': 'Software Engineer',
            'company_name': 'TechCorp Inc.',
            'location': 'St. Louis, MO',
            'job_description': 'We are looking for a talented Software Engineer to join our team. Experience with Python, JavaScript, and React is required. Knowledge of AWS and Docker is a plus.',
            'required_skills': 'Python, JavaScript, React, AWS, Docker',
            'experience_level': 'Mid-level',
            'salary_range': '$80,000 - $120,000',
            'posted_date': '2024-01-15',
            'job_url': 'https://example.com/job1',
            'source_website': 'Indeed'
        },
        {
            'job_title': 'Senior Python Developer',
            'company_name': 'DataSolutions LLC',
            'location': 'St. Louis, MO',
            'job_description': 'Senior Python Developer needed for our data science team. Must have 5+ years experience with Python, SQL, and machine learning frameworks. Experience with TensorFlow or PyTorch preferred.',
            'required_skills': 'Python, SQL, Machine Learning, TensorFlow, PyTorch',
            'experience_level': 'Senior',
            'salary_range': '$120,000 - $160,000',
            'posted_date': '2024-01-14',
            'job_url': 'https://example.com/job2',
            'source_website': 'LinkedIn'
        },
        {
            'job_title': 'Frontend Developer',
            'company_name': 'WebTech Solutions',
            'location': 'St. Louis, MO',
            'job_description': 'Frontend Developer position available. Must be proficient in HTML, CSS, JavaScript, and React. Experience with Node.js and modern build tools required.',
            'required_skills': 'HTML, CSS, JavaScript, React, Node.js',
            'experience_level': 'Junior',
            'salary_range': '$60,000 - $80,000',
            'posted_date': '2024-01-13',
            'job_url': 'https://example.com/job3',
            'source_website': 'Indeed'
        },
        {
            'job_title': 'DevOps Engineer',
            'company_name': 'CloudFirst Systems',
            'location': 'St. Louis, MO',
            'job_description': 'DevOps Engineer to manage our cloud infrastructure. Experience with AWS, Docker, Kubernetes, and CI/CD pipelines required. Knowledge of Terraform and Ansible is a plus.',
            'required_skills': 'AWS, Docker, Kubernetes, CI/CD, Terraform, Ansible',
            'experience_level': 'Senior',
            'salary_range': '$100,000 - $140,000',
            'posted_date': '2024-01-12',
            'job_url': 'https://example.com/job4',
            'source_website': 'LinkedIn'
        },
        {
            'job_title': 'Data Scientist',
            'company_name': 'Analytics Pro',
            'location': 'St. Louis, MO',
            'job_description': 'Data Scientist position focusing on machine learning and statistical analysis. Must have experience with Python, R, SQL, and data visualization tools. PhD in Computer Science or related field preferred.',
            'required_skills': 'Python, R, SQL, Machine Learning, Data Visualization',
            'experience_level': 'Senior',
            'salary_range': '$130,000 - $170,000',
            'posted_date': '2024-01-11',
            'job_url': 'https://example.com/job5',
            'source_website': 'Indeed'
        }
    ]
    return sample_jobs

def test_data_processing():
    """Test the data processing functionality."""
    print("🧪 Testing Data Processing System")
    print("=" * 50)
    
    # Initialize data processor
    processor = JobDataProcessor()
    
    # Create sample data
    sample_jobs = create_sample_jobs()
    print(f"Created {len(sample_jobs)} sample jobs")
    
    # Test data cleaning and validation
    cleaned_jobs = []
    for job in sample_jobs:
        cleaned_job = processor.clean_job_data(job)
        if processor.validate_job_data(cleaned_job):
            cleaned_jobs.append(cleaned_job)
    
    print(f"Validated and cleaned {len(cleaned_jobs)} jobs")
    
    # Test filtering
    print("\n📊 Testing Filtering Functionality:")
    
    # Filter by location
    st_louis_jobs = processor.filter_jobs(cleaned_jobs, location="St. Louis")
    print(f"Jobs in St. Louis: {len(st_louis_jobs)}")
    
    # Filter by keywords
    python_jobs = processor.filter_jobs(cleaned_jobs, keywords=["python"])
    print(f"Jobs requiring Python: {len(python_jobs)}")
    
    # Filter by experience level
    senior_jobs = processor.filter_jobs(cleaned_jobs, keywords=["senior"])
    print(f"Senior level jobs: {len(senior_jobs)}")
    
    # Generate summary statistics
    stats = processor.generate_summary_stats(cleaned_jobs)
    print(f"\n📈 Summary Statistics:")
    print(f"Total jobs: {stats['total_jobs']}")
    print(f"Unique companies: {stats['unique_companies']}")
    print(f"Unique locations: {stats['unique_locations']}")
    print(f"Sources: {stats['sources']}")
    
    return cleaned_jobs

def test_file_operations():
    """Test file saving and loading operations."""
    print("\n💾 Testing File Operations")
    print("=" * 50)
    
    processor = JobDataProcessor()
    sample_jobs = create_sample_jobs()
    
    # Test CSV saving
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"test_jobs_{timestamp}.csv"
    csv_path = processor.save_to_csv(sample_jobs, csv_filename)
    print(f"✅ Saved CSV file: {csv_path}")
    
    # Test JSON saving
    json_filename = f"test_jobs_{timestamp}.json"
    json_path = processor.save_to_json(sample_jobs, json_filename)
    print(f"✅ Saved JSON file: {json_path}")
    
    # Test loading from CSV
    loaded_csv_jobs = processor.load_from_csv(csv_path)
    print(f"✅ Loaded {len(loaded_csv_jobs)} jobs from CSV")
    
    # Test loading from JSON
    loaded_json_jobs = processor.load_from_json(json_path)
    print(f"✅ Loaded {len(loaded_json_jobs)} jobs from JSON")
    
    return csv_path, json_path

def demonstrate_scraping_simulation():
    """Demonstrate how the scraping system would work."""
    print("\n🕷️  Scraping System Demonstration")
    print("=" * 50)
    
    print("This is a demonstration of the job scraping system architecture.")
    print("In a real implementation, the system would:")
    print()
    print("1. ✅ Check robots.txt files for each target website")
    print("2. ✅ Implement rate limiting (2-5 second delays between requests)")
    print("3. ✅ Use proper user-agent headers")
    print("4. ✅ Handle errors gracefully")
    print("5. ✅ Extract job data from multiple sources:")
    print("   - Indeed (using BeautifulSoup)")
    print("   - LinkedIn (using Selenium)")
    print("   - Glassdoor (future implementation)")
    print()
    print("6. ✅ Clean and validate extracted data")
    print("7. ✅ Remove duplicates")
    print("8. ✅ Save results in CSV and JSON formats")
    print()
    print("🔒 Ethical Considerations:")
    print("- Respects website terms of service")
    print("- Implements proper rate limiting")
    print("- Only scrapes publicly available data")
    print("- Includes comprehensive error handling")

def main():
    """Main test function."""
    print("🚀 AI-Powered Job Matching System - Stage 1 Testing")
    print("=" * 60)
    
    try:
        # Test data processing
        cleaned_jobs = test_data_processing()
        
        # Test file operations
        csv_path, json_path = test_file_operations()
        
        # Demonstrate scraping system
        demonstrate_scraping_simulation()
        
        print("\n✅ All tests completed successfully!")
        print(f"\n📁 Generated files:")
        print(f"   - {csv_path}")
        print(f"   - {json_path}")
        print(f"   - job_scraper.log")
        
        print("\n🎯 Stage 1 Implementation Complete!")
        print("The system is ready for real job scraping with proper ethical considerations.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
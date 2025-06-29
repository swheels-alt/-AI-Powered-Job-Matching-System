#!/usr/bin/env python3
"""
Stage 2: Data Preprocessing Script
Demonstrates the complete preprocessing pipeline for job data and resume text.
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from preprocessing.embedding_preparer import EmbeddingPreparer
from preprocessing.text_cleaner import TextCleaner
from preprocessing.data_preprocessor import DataPreprocessor
from preprocessing.resume_parser import ResumeParser
from utils.data_processor import JobDataProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_sample_resume():
    """Create a sample resume for testing."""
    sample_resume = """
JOHN DOE
Software Engineer
john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe | github.com/johndoe

SUMMARY
Experienced software engineer with 5+ years of experience in full-stack development. 
Proficient in Python, JavaScript, React, and Node.js. Passionate about creating 
scalable web applications and solving complex technical challenges.

EXPERIENCE
Senior Software Engineer
TechCorp Inc. | 2022 - Present
- Developed and maintained RESTful APIs using Python and Django
- Led a team of 3 developers in building a customer portal
- Implemented CI/CD pipelines using Jenkins and Docker
- Reduced application load time by 40% through optimization

Software Developer
StartupXYZ | 2020 - 2022
- Built responsive web applications using React and Node.js
- Collaborated with UX designers to implement user-friendly interfaces
- Integrated third-party APIs for payment processing
- Participated in agile development processes

EDUCATION
Bachelor of Science in Computer Science
University of Technology | 2016 - 2020
- GPA: 3.8/4.0
- Relevant coursework: Data Structures, Algorithms, Database Systems

SKILLS
Programming Languages: Python, JavaScript, TypeScript, Java, SQL
Frameworks & Libraries: React, Node.js, Django, Express, Bootstrap
Tools & Technologies: Git, Docker, AWS, Jenkins, MongoDB, PostgreSQL
Methodologies: Agile, Scrum, Test-Driven Development, CI/CD

PROJECTS
E-Commerce Platform
- Built a full-stack e-commerce application using React and Node.js
- Implemented user authentication, payment processing, and inventory management
- Deployed on AWS with Docker containerization

Task Management App
- Developed a collaborative task management tool using Python and Django
- Features include real-time updates, file sharing, and team collaboration
- Integrated with Slack for notifications

CERTIFICATIONS
AWS Certified Developer Associate
Google Cloud Platform Certified
    """
    return sample_resume

def demonstrate_text_cleaning():
    """Demonstrate text cleaning functionality."""
    print("🧹 Text Cleaning Demonstration")
    print("=" * 50)
    
    text_cleaner = TextCleaner()
    
    # Sample text with HTML and special characters
    sample_text = """
    <p>We are looking for a <strong>Senior Software Engineer</strong> to join our team!</p>
    <ul>
        <li>Experience with Python & JavaScript required</li>
        <li>Knowledge of AWS, Docker, and Kubernetes a plus</li>
    </ul>
    <p>Location: St. Louis, MO. Salary: $80,000 - $120,000</p>
    """
    
    print("Original text:")
    print(sample_text)
    print("\nCleaned text:")
    cleaned_text = text_cleaner.clean_html(sample_text)
    print(cleaned_text)
    
    print("\nNormalized location:")
    location = "st. louis, mo."
    normalized_location = text_cleaner.normalize_location(location)
    print(f"{location} -> {normalized_location}")
    
    print("\nNormalized job title:")
    title = "sr. software eng."
    normalized_title = text_cleaner.normalize_job_title(title)
    print(f"{title} -> {normalized_title}")
    
    print("\nExtracted skills:")
    skills = text_cleaner.extract_skills(sample_text)
    print(f"Found skills: {', '.join(skills)}")

def demonstrate_data_preprocessing():
    """Demonstrate data preprocessing functionality."""
    print("\n📊 Data Preprocessing Demonstration")
    print("=" * 50)
    
    # Load sample job data
    data_processor = JobDataProcessor()
    sample_jobs = data_processor.load_from_json("data/raw/test_jobs_20250629_173208.json")
    
    print(f"Loaded {len(sample_jobs)} sample jobs")
    
    # Initialize preprocessor
    preprocessor = DataPreprocessor()
    
    # Preprocess jobs
    preprocessed_jobs = preprocessor.preprocess_job_data(
        sample_jobs,
        remove_stop_words=False,
        lemmatize=False,
        extract_skills=True
    )
    
    print(f"Preprocessed {len(preprocessed_jobs)} jobs")
    
    # Show example of preprocessed job
    if preprocessed_jobs:
        example_job = preprocessed_jobs[0]
        print("\nExample preprocessed job:")
        print(f"Title: {example_job.get('job_title', 'N/A')}")
        print(f"Company: {example_job.get('company_name', 'N/A')}")
        print(f"Location: {example_job.get('location', 'N/A')}")
        print(f"Experience Level: {example_job.get('experience_level', 'N/A')}")
        print(f"Extracted Skills: {', '.join(example_job.get('extracted_skills', []))}")
        print(f"Description Length: {len(example_job.get('job_description', ''))} characters")
    
    # Generate preprocessing report
    report = preprocessor.generate_preprocessing_report(sample_jobs, preprocessed_jobs)
    print(f"\nPreprocessing Report:")
    print(f"- Original jobs: {report['original_count']}")
    print(f"- Preprocessed jobs: {report['preprocessed_count']}")
    print(f"- Removal rate: {report['removal_rate']:.1f}%")
    print(f"- Average description length: {report['average_description_length']:.0f} characters")
    print(f"- Total skills found: {report['skills_extraction_stats']['total_skills_found']}")
    print(f"- Average skills per job: {report['skills_extraction_stats']['average_skills_per_job']:.1f}")
    
    return preprocessed_jobs

def demonstrate_resume_parsing():
    """Demonstrate resume parsing functionality."""
    print("\n📄 Resume Parsing Demonstration")
    print("=" * 50)
    
    resume_parser = ResumeParser()
    sample_resume = create_sample_resume()
    
    print("Sample resume length:", len(sample_resume), "characters")
    
    # Parse resume
    parsed_resume = resume_parser.parse_resume_text(sample_resume)
    
    print(f"Parsed {len(parsed_resume)} sections:")
    for section_name, section_data in parsed_resume.items():
        if isinstance(section_data, dict) and 'word_count' in section_data:
            print(f"- {section_name}: {section_data['word_count']} words")
    
    # Show contact information
    if 'contact_info' in parsed_resume:
        contact = parsed_resume['contact_info']
        print(f"\nContact Information:")
        for key, value in contact.items():
            print(f"- {key}: {value}")
    
    # Show extracted skills
    if 'extracted_skills' in parsed_resume:
        skills = parsed_resume['extracted_skills']
        print(f"\nExtracted Skills ({len(skills)} total):")
        print(f"- {', '.join(skills[:10])}...")  # Show first 10 skills
    
    # Generate resume summary
    summary = resume_parser.generate_resume_summary(parsed_resume)
    print(f"\nResume Summary:")
    print(f"- Total sections: {summary['total_sections']}")
    print(f"- Total skills: {summary['total_skills']}")
    print(f"- Has contact info: {summary['has_contact_info']}")
    
    return parsed_resume

def demonstrate_embedding_preparation():
    """Demonstrate embedding preparation functionality."""
    print("\n🔗 Embedding Preparation Demonstration")
    print("=" * 50)
    
    # Load sample job data
    data_processor = JobDataProcessor()
    sample_jobs = data_processor.load_from_json("data/raw/test_jobs_20250629_173208.json")
    
    # Create sample resume
    sample_resume = create_sample_resume()
    
    # Initialize embedding preparer
    embedding_preparer = EmbeddingPreparer()
    
    # Create embedding batch
    preprocessing_config = {
        'jobs': {
            'remove_stop_words': False,
            'lemmatize': False,
            'extract_skills': True,
            'missing_data_strategy': 'fill_na'
        },
        'resume': {
            'remove_stop_words': False,
            'lemmatize': False,
            'include_sections': ['summary', 'experience', 'skills', 'education', 'projects']
        }
    }
    
    embedding_batch = embedding_preparer.create_embedding_batch(
        sample_jobs, sample_resume, preprocessing_config
    )
    
    print(f"Created embedding batch with {len(embedding_batch['jobs'])} jobs")
    print(f"Resume included: {embedding_batch['resume'] is not None}")
    
    # Show batch statistics
    stats = embedding_batch['statistics']
    print(f"\nBatch Statistics:")
    print(f"- Total jobs: {stats['total_jobs']}")
    print(f"- Jobs with skills: {stats['jobs_with_skills']}")
    print(f"- Average job description length: {stats['average_job_description_length']:.0f} characters")
    print(f"- Resume included: {stats['resume_included']}")
    
    # Show example embedding text
    if embedding_batch['jobs']:
        example_job = embedding_batch['jobs'][0]
        embedding_text = example_job['embedding_text']
        print(f"\nExample Job Embedding Text (first 200 chars):")
        print(f"'{embedding_text[:200]}...'")
    
    if embedding_batch['resume']:
        resume_embedding_text = embedding_batch['resume']['embedding_text']
        print(f"\nResume Embedding Text (first 200 chars):")
        print(f"'{resume_embedding_text[:200]}...'")
    
    # Validate embedding batch
    is_valid = embedding_preparer.validate_embedding_batch(embedding_batch)
    print(f"\nEmbedding batch validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Save embedding batch
    filepath = embedding_preparer.save_embedding_batch(embedding_batch)
    print(f"Saved embedding batch to: {filepath}")
    
    return embedding_batch

def demonstrate_missing_data_handling():
    """Demonstrate missing data handling strategies."""
    print("\n🔧 Missing Data Handling Demonstration")
    print("=" * 50)
    
    # Create sample data with missing fields
    incomplete_jobs = [
        {
            'job_title': 'Software Engineer',
            'company_name': 'TechCorp Inc.',
            'location': 'St. Louis, MO',
            'job_description': 'We are looking for a talented Software Engineer.',
            # Missing: required_skills, experience_level, salary_range
        },
        {
            'job_title': 'Data Scientist',
            'company_name': 'DataCorp',
            'location': '',  # Missing location
            'job_description': 'Data Scientist position available.',
            'required_skills': 'Python, SQL, Machine Learning',
            'experience_level': 'Senior',
            'salary_range': '$100,000 - $150,000'
        }
    ]
    
    preprocessor = DataPreprocessor()
    
    print("Original incomplete jobs:")
    for i, job in enumerate(incomplete_jobs):
        missing_fields = [field for field in ['job_title', 'company_name', 'location', 'job_description'] 
                         if not job.get(field)]
        print(f"Job {i+1}: Missing {missing_fields}")
    
    # Test different strategies
    strategies = ['fill_na', 'remove']
    
    for strategy in strategies:
        print(f"\nStrategy: {strategy}")
        processed_jobs = preprocessor.handle_missing_data(incomplete_jobs, strategy)
        print(f"Result: {len(processed_jobs)} jobs")
        
        if processed_jobs:
            example_job = processed_jobs[0]
            print(f"Example - Location: '{example_job.get('location', 'N/A')}'")
            print(f"Example - Skills: '{example_job.get('required_skills', 'N/A')}'")

def main():
    """Main function to demonstrate Stage 2 preprocessing."""
    print("🚀 Stage 2: Data Preprocessing Demonstration")
    print("=" * 60)
    
    try:
        # Demonstrate text cleaning
        demonstrate_text_cleaning()
        
        # Demonstrate data preprocessing
        preprocessed_jobs = demonstrate_data_preprocessing()
        
        # Demonstrate resume parsing
        parsed_resume = demonstrate_resume_parsing()
        
        # Demonstrate embedding preparation
        embedding_batch = demonstrate_embedding_preparation()
        
        # Demonstrate missing data handling
        demonstrate_missing_data_handling()
        
        print("\n" + "=" * 60)
        print("✅ Stage 2 Preprocessing Complete!")
        print("\nThe system now includes:")
        print("✅ Comprehensive text cleaning and normalization")
        print("✅ Job data preprocessing with skill extraction")
        print("✅ Resume parsing and section extraction")
        print("✅ Missing data handling strategies")
        print("✅ Embedding text preparation")
        print("✅ Data validation and quality checks")
        print("✅ Comprehensive reporting and statistics")
        
        print(f"\n📁 Generated files:")
        print(f"   - data/processed/embedding_batch_*.json")
        print(f"   - data/processed/preprocessed_jobs_*.json")
        
        print("\n🎯 Ready for Stage 3: Embedding Generation!")
        
    except Exception as e:
        logger.error(f"Error in preprocessing demonstration: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
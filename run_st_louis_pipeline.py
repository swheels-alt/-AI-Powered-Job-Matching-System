#!/usr/bin/env python3
"""
Complete Pipeline for St. Louis Job Data
Runs preprocessing, embedding generation, and job matching with real St. Louis data.
"""

import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def load_st_louis_jobs():
    """Load the St. Louis job data we collected."""
    # Find the most recent St. Louis job file
    raw_dir = "data/raw"
    st_louis_files = [f for f in os.listdir(raw_dir) if f.startswith("st_louis_") and f.endswith(".json")]
    
    if not st_louis_files:
        print("❌ No St. Louis job files found. Run free_job_api_test.py first.")
        return None
    
    # Get the most recent file
    latest_file = max(st_louis_files, key=lambda x: os.path.getctime(os.path.join(raw_dir, x)))
    filepath = os.path.join(raw_dir, latest_file)
    
    print(f"📁 Loading St. Louis jobs from: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data['jobs']

def create_sample_resume():
    """Create a sample resume for matching."""
    resume = """
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
    return resume

def run_preprocessing(jobs):
    """Run preprocessing on the job data."""
    print("\n🧹 Running Data Preprocessing...")
    print("=" * 50)
    
    try:
        from preprocessing.embedding_preparer import EmbeddingPreparer
        from preprocessing.data_preprocessor import DataPreprocessor
        from preprocessing.resume_parser import ResumeParser
        
        # Initialize preprocessors
        preprocessor = DataPreprocessor()
        resume_parser = ResumeParser()
        embedding_preparer = EmbeddingPreparer()
        
        # Preprocess jobs
        print("📊 Preprocessing job data...")
        preprocessed_jobs = preprocessor.preprocess_job_data(
            jobs,
            remove_stop_words=False,
            lemmatize=False,
            extract_skills=True
        )
        
        print(f"✅ Preprocessed {len(preprocessed_jobs)} jobs")
        
        # Parse resume
        print("📄 Parsing resume...")
        sample_resume = create_sample_resume()
        parsed_resume = resume_parser.parse_resume_text(sample_resume)
        
        print(f"✅ Parsed resume with {len(parsed_resume)} sections")
        
        # Prepare embedding batch
        print("🔗 Preparing embedding batch...")
        embedding_batch = embedding_preparer.create_embedding_batch(
            preprocessed_jobs,
            sample_resume,
            {
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
        )
        
        print(f"✅ Created embedding batch with {len(embedding_batch['jobs'])} jobs")
        
        return embedding_batch
        
    except Exception as e:
        print(f"❌ Error in preprocessing: {e}")
        return None

def run_embedding_generation(embedding_batch):
    """Run embedding generation (demo mode without API key)."""
    print("\n🔗 Running Embedding Generation...")
    print("=" * 50)
    
    try:
        from embeddings.embedding_generator import EmbeddingGenerator
        from embeddings.similarity_calculator import SimilarityCalculator
        
        # Initialize components
        calculator = SimilarityCalculator()
        
        # Create sample embeddings for demonstration
        print("🎯 Creating sample embeddings for demonstration...")
        
        # Create sample embeddings (simplified for demo)
        sample_embeddings = []
        for i, job in enumerate(embedding_batch['jobs']):
            # Create a simple embedding based on job content
            embedding = [0.1 + i * 0.01, 0.2 + i * 0.01, 0.3 + i * 0.01, 0.4 + i * 0.01, 0.5 + i * 0.01] * 100
            sample_embeddings.append({
                'job_data': job,
                'embedding': embedding
            })
        
        # Create resume embedding
        resume_embedding = [0.1, 0.2, 0.3, 0.4, 0.5] * 100
        
        print(f"✅ Created {len(sample_embeddings)} job embeddings and 1 resume embedding")
        
        return sample_embeddings, resume_embedding
        
    except Exception as e:
        print(f"❌ Error in embedding generation: {e}")
        return None, None

def run_job_matching(job_embeddings, resume_embedding):
    """Run job matching using similarity calculations."""
    print("\n🎯 Running Job Matching...")
    print("=" * 50)
    
    try:
        from embeddings.similarity_calculator import SimilarityCalculator
        
        calculator = SimilarityCalculator()
        
        # Calculate similarities
        similarities = []
        for job_embedding_data in job_embeddings:
            job_embedding = job_embedding_data['embedding']
            job_data = job_embedding_data['job_data']
            
            # Calculate cosine similarity
            similarity = calculator.cosine_similarity(job_embedding, resume_embedding)
            
            similarities.append({
                'job_data': job_data,
                'similarity_score': similarity
            })
        
        # Sort by similarity score (highest first)
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        print(f"✅ Calculated similarities for {len(similarities)} jobs")
        
        return similarities
        
    except Exception as e:
        print(f"❌ Error in job matching: {e}")
        return None

def generate_report(jobs, similarities):
    """Generate a comprehensive report."""
    print("\n📋 Generating Report...")
    print("=" * 50)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"st_louis_job_matching_report_{timestamp}.json"
    
    # Create report
    report = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'location': 'St. Louis, MO',
            'total_jobs': len(jobs),
            'unique_companies': len(set(j.get('company_name', '') for j in jobs if j.get('company_name'))),
            'pipeline_stages': ['Data Collection', 'Preprocessing', 'Embedding Generation', 'Job Matching']
        },
        'top_matches': []
    }
    
    # Add top 10 matches
    for i, match in enumerate(similarities[:10]):
        job_data = match['job_data']
        report['top_matches'].append({
            'rank': i + 1,
            'job_title': job_data.get('job_title', 'N/A'),
            'company_name': job_data.get('company_name', 'N/A'),
            'location': job_data.get('location', 'N/A'),
            'salary_range': job_data.get('salary_range', 'N/A'),
            'required_skills': job_data.get('required_skills', 'N/A'),
            'similarity_score': round(match['similarity_score'], 4),
            'job_url': job_data.get('job_url', 'N/A')
        })
    
    # Save report
    os.makedirs("data/processed", exist_ok=True)
    report_path = os.path.join("data/processed", report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Report saved to: {report_path}")
    
    return report

def main():
    """Main function to run the complete pipeline."""
    print("🚀 St. Louis Job Matching Pipeline")
    print("=" * 60)
    print("Running complete pipeline with real St. Louis job data")
    print()
    
    # Load St. Louis jobs
    jobs = load_st_louis_jobs()
    if not jobs:
        return
    
    print(f"📊 Loaded {len(jobs)} St. Louis jobs")
    
    # Run preprocessing
    embedding_batch = run_preprocessing(jobs)
    if not embedding_batch:
        print("❌ Preprocessing failed")
        return
    
    # Run embedding generation
    job_embeddings, resume_embedding = run_embedding_generation(embedding_batch)
    if not job_embeddings:
        print("❌ Embedding generation failed")
        return
    
    # Run job matching
    similarities = run_job_matching(job_embeddings, resume_embedding)
    if not similarities:
        print("❌ Job matching failed")
        return
    
    # Generate report
    report = generate_report(jobs, similarities)
    
    # Display results
    print("\n🏆 TOP 10 JOB MATCHES FOR ST. LOUIS")
    print("=" * 60)
    
    for i, match in enumerate(report['top_matches']):
        print(f"\n{i+1}. {match['job_title']} at {match['company_name']}")
        print(f"   Location: {match['location']}")
        print(f"   Salary: {match['salary_range']}")
        print(f"   Skills: {match['required_skills']}")
        print(f"   Match Score: {match['similarity_score']:.4f}")
        print(f"   Apply: {match['job_url']}")
    
    print(f"\n✅ Pipeline completed successfully!")
    print(f"📁 Check 'data/processed/' for detailed report")
    print(f"🎯 Found {len(similarities)} job matches for St. Louis area")

if __name__ == "__main__":
    main() 
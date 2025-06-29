#!/usr/bin/env python3
"""
Stage 3: Embedding Generation Script
Demonstrates the complete embedding generation pipeline for job data and resume text.
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from embeddings.embedding_generator import EmbeddingGenerator
from embeddings.openai_embedder import OpenAIEmbedder
from embeddings.embedding_manager import EmbeddingManager
from embeddings.similarity_calculator import SimilarityCalculator
from preprocessing.embedding_preparer import EmbeddingPreparer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_sample_embedding_batch():
    """Create a sample embedding batch for testing without API calls."""
    sample_batch = {
        'jobs': [
            {
                'job_title': 'Software Engineer',
                'company_name': 'TechCorp Inc.',
                'location': 'Saint Louis, MO',
                'embedding_text': 'Software Engineer TechCorp Inc. we are looking for a talented software engineer to join our team. experience with python, javascript, and react is required. knowledge of aws and docker is a plus. docker javascript aws java react python r mid-level',
                'extracted_skills': ['docker', 'javascript', 'aws', 'java', 'react', 'python', 'r'],
                'experience_level': 'mid-level'
            },
            {
                'job_title': 'Senior Python Developer',
                'company_name': 'DataSolutions LLC',
                'location': 'Saint Louis, MO',
                'embedding_text': 'Senior Python Developer DataSolutions LLC senior python developer needed for our data science team. must have 5 years experience with python, sql, and machine learning frameworks. experience with tensorflow or pytorch preferred. data science tensorflow sql python r pytorch machine learning senior',
                'extracted_skills': ['data science', 'tensorflow', 'sql', 'python', 'r', 'pytorch', 'machine learning'],
                'experience_level': 'senior'
            },
            {
                'job_title': 'Frontend Developer',
                'company_name': 'WebTech Solutions',
                'location': 'Saint Louis, MO',
                'embedding_text': 'Frontend Developer WebTech Solutions frontend developer position available. must be proficient in html, css, javascript, and react. experience with node.js and modern build tools required. ml html node.js javascript java react js css r ai junior',
                'extracted_skills': ['ml', 'html', 'node.js', 'javascript', 'java', 'react', 'js', 'css', 'r', 'ai'],
                'experience_level': 'junior'
            }
        ],
        'resume': {
            'embedding_text': 'experienced software engineer with 5 years of experience in full-stack development. proficient in python, javascript, react, and node.js. passionate about creating scalable web applications and solving complex technical challenges. senior software engineer techcorp inc. 2022 - present - developed and maintained restful apis using python and django - led a team of 3 developers in building a customer portal - implemented ci/cd pipelines using jenkins and docker - reduced application load time by 40 through optimization software developer startupxyz 2020 - 2022 - built responsive web applications using react and node.js - collaborated with ux designers to implement user-friendly interfaces - integrated third-party apis for payment processing - participated in agile development processes bachelor of science in computer science university of technology 2016 - 2020 - gpa: 3.8/4.0 - relevant coursework: data structures, algorithms, database systems programming languages: python, javascript, typescript, java, sql frameworks libraries: react, node.js, django, express, bootstrap tools technologies: git, docker, aws, jenkins, mongodb, postgresql methodologies: agile, scrum, test-driven development, ci/cd e-commerce platform - built a full-stack e-commerce application using react and node.js - implemented user authentication, payment processing, and inventory management - deployed on aws with docker containerization task management app - developed a collaborative task management tool using python and django - features include real-time updates, file sharing, and team collaboration - integrated with slack for notifications aws certified developer associate google cloud platform certified',
            'parsed_resume': {
                'contact_info': {
                    'email': 'john.doe@email.com',
                    'phone': '(555) 123-4567',
                    'linkedin': 'linkedin.com/in/johndoe',
                    'github': 'github.com/johndoe'
                }
            }
        },
        'batch_created_at': datetime.now().isoformat(),
        'preprocessing_config': {
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
        },
        'statistics': {
            'total_jobs': 3,
            'jobs_with_skills': 3,
            'average_job_description_length': 200,
            'resume_included': True
        }
    }
    return sample_batch

def demonstrate_embedding_generator():
    """Demonstrate embedding generator functionality."""
    print("🔗 Embedding Generator Demonstration")
    print("=" * 50)
    
    # Initialize embedding generator (without API key for demo)
    try:
        generator = EmbeddingGenerator(model="text-embedding-3-small")
        print(f"✅ Initialized embedding generator with model: {generator.embedder.model}")
    except ValueError as e:
        print(f"⚠️  API key not provided: {e}")
        print("   This is expected for demonstration purposes")
        return None
    
    # Test embedding pipeline
    print("\n🧪 Testing embedding pipeline...")
    if generator.test_embedding_pipeline():
        print("✅ All embedding pipeline tests passed")
    else:
        print("❌ Some embedding pipeline tests failed")
    
    return generator

def demonstrate_similarity_calculator():
    """Demonstrate similarity calculation functionality."""
    print("\n📊 Similarity Calculator Demonstration")
    print("=" * 50)
    
    calculator = SimilarityCalculator()
    
    # Create sample embeddings (simplified for demo)
    embedding1 = [0.1, 0.2, 0.3, 0.4, 0.5]
    embedding2 = [0.1, 0.2, 0.3, 0.4, 0.5]  # Identical to embedding1
    embedding3 = [0.9, 0.8, 0.7, 0.6, 0.5]  # Different from embedding1
    
    print("Sample embeddings created:")
    print(f"Embedding 1: {embedding1}")
    print(f"Embedding 2: {embedding2} (identical to 1)")
    print(f"Embedding 3: {embedding3} (different from 1)")
    
    # Calculate similarities
    print("\nSimilarity calculations:")
    
    # Cosine similarity
    cos_sim_12 = calculator.cosine_similarity(embedding1, embedding2)
    cos_sim_13 = calculator.cosine_similarity(embedding1, embedding3)
    print(f"Cosine similarity (1,2): {cos_sim_12:.4f}")
    print(f"Cosine similarity (1,3): {cos_sim_13:.4f}")
    
    # Euclidean distance
    euc_dist_12 = calculator.euclidean_distance(embedding1, embedding2)
    euc_dist_13 = calculator.euclidean_distance(embedding1, embedding3)
    print(f"Euclidean distance (1,2): {euc_dist_12:.4f}")
    print(f"Euclidean distance (1,3): {euc_dist_13:.4f}")
    
    # All similarities
    all_sims = calculator.calculate_all_similarities(embedding1, embedding3)
    print(f"\nAll similarity metrics (1,3):")
    for metric, value in all_sims.items():
        print(f"  {metric}: {value:.4f}")
    
    # Find most similar
    candidates = [embedding1, embedding2, embedding3]
    most_similar = calculator.find_most_similar(embedding1, candidates, top_k=2)
    print(f"\nMost similar to embedding 1:")
    for index, score in most_similar:
        print(f"  Index {index}: {score:.4f}")
    
    # Embedding statistics
    stats = calculator.calculate_embedding_statistics(candidates)
    print(f"\nEmbedding statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    return calculator

def demonstrate_embedding_manager():
    """Demonstrate embedding manager functionality."""
    print("\n💾 Embedding Manager Demonstration")
    print("=" * 50)
    
    # Initialize embedding manager
    manager = EmbeddingManager(storage_dir="data/embeddings_demo")
    
    # Create sample embedding data
    sample_text = "Software Engineer with Python and JavaScript experience"
    sample_embedding = [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # 500-dimensional embedding
    sample_metadata = {
        'job_title': 'Software Engineer',
        'company_name': 'Demo Corp',
        'location': 'Demo City, DC'
    }
    
    print(f"Sample text: {sample_text}")
    print(f"Sample embedding dimensions: {len(sample_embedding)}")
    
    # Save embedding
    embedding_id = manager.save_embedding(sample_text, sample_embedding, "text-embedding-3-small", sample_metadata)
    print(f"✅ Saved embedding with ID: {embedding_id}")
    
    # Load embedding
    loaded_data = manager.load_embedding(embedding_id)
    if loaded_data:
        print(f"✅ Loaded embedding:")
        print(f"  Text: {loaded_data['text'][:50]}...")
        print(f"  Model: {loaded_data['model']}")
        print(f"  Dimensions: {loaded_data['dimension']}")
        print(f"  Metadata: {loaded_data['metadata']}")
    
    # Get storage statistics
    stats = manager.get_storage_stats()
    print(f"\nStorage statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Clean up demo embedding
    manager.delete_embedding(embedding_id)
    print(f"✅ Cleaned up demo embedding")
    
    return manager

def demonstrate_openai_embedder():
    """Demonstrate OpenAI embedder functionality."""
    print("\n🤖 OpenAI Embedder Demonstration")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  No OpenAI API key found in environment")
        print("   Set OPENAI_API_KEY environment variable to test API functionality")
        print("   Skipping API tests for demonstration")
        return None
    
    try:
        # Initialize embedder
        embedder = OpenAIEmbedder(api_key=api_key, model="text-embedding-3-small")
        print(f"✅ Initialized OpenAI embedder with model: {embedder.model}")
        
        # Test connection
        print("\n🧪 Testing API connection...")
        if embedder.test_connection():
            print("✅ API connection successful")
        else:
            print("❌ API connection failed")
            return None
        
        # Test single embedding
        test_text = "Software Engineer with Python and JavaScript experience"
        print(f"\n📝 Testing single embedding for: '{test_text}'")
        embedding = embedder.embed_text(test_text)
        if embedding:
            print(f"✅ Generated embedding with {len(embedding)} dimensions")
            print(f"   First 5 values: {embedding[:5]}")
        else:
            print("❌ Failed to generate embedding")
        
        # Get usage statistics
        usage_stats = embedder.get_usage_stats()
        print(f"\n📊 Usage statistics:")
        for key, value in usage_stats.items():
            print(f"  {key}: {value}")
        
        return embedder
        
    except Exception as e:
        print(f"❌ Error initializing OpenAI embedder: {e}")
        return None

def demonstrate_complete_pipeline():
    """Demonstrate the complete embedding pipeline."""
    print("\n🚀 Complete Embedding Pipeline Demonstration")
    print("=" * 50)
    
    # Create sample embedding batch
    embedding_batch = create_sample_embedding_batch()
    print(f"✅ Created sample embedding batch with {len(embedding_batch['jobs'])} jobs")
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("\n⚠️  No OpenAI API key found - demonstrating pipeline structure only")
        print("   Set OPENAI_API_KEY environment variable to test full functionality")
        
        # Show what would happen with API
        print("\n📋 Pipeline steps that would be executed:")
        print("1. Initialize embedding generator")
        print("2. Generate embeddings for job texts")
        print("3. Generate embedding for resume text")
        print("4. Store embeddings with metadata")
        print("5. Calculate similarity scores")
        print("6. Find most similar jobs")
        
        return
    
    try:
        # Initialize embedding generator
        generator = EmbeddingGenerator(api_key=api_key, model="text-embedding-3-small")
        print(f"✅ Initialized embedding generator")
        
        # Generate embeddings from batch
        print("\n🔄 Generating embeddings from batch...")
        results = generator.generate_embeddings_from_batch(embedding_batch, batch_size=10)
        
        print(f"✅ Embedding generation completed:")
        print(f"  Job embeddings: {len(results['job_embedding_ids'])}")
        print(f"  Resume embedding: {results['resume_embedding_id']}")
        print(f"  Model used: {results['model']}")
        
        # Show usage statistics
        usage_stats = results['usage_stats']
        print(f"\n📊 API Usage:")
        print(f"  Requests: {usage_stats['request_count']}")
        print(f"  Total tokens: {usage_stats['total_tokens']}")
        print(f"  Total cost: ${usage_stats['total_cost_usd']:.6f}")
        
        # Find similar jobs
        if results['resume_embedding_id']:
            print(f"\n🔍 Finding similar jobs...")
            similar_jobs = generator.find_similar_jobs(
                results['resume_embedding_id'], 
                top_k=3, 
                similarity_metric='cosine_similarity'
            )
            
            print(f"✅ Found {len(similar_jobs)} similar jobs:")
            for i, job in enumerate(similar_jobs, 1):
                print(f"  {i}. {job['job_title']} at {job['company_name']}")
                print(f"     Location: {job['location']}")
                print(f"     Similarity: {job['similarity_score']:.4f}")
        
        # Get comprehensive statistics
        stats = generator.get_embedding_statistics()
        print(f"\n📈 Comprehensive Statistics:")
        print(f"  Storage: {stats['storage']['total_embeddings']} embeddings")
        print(f"  Job embeddings: {stats['job_embeddings']['valid_count']}")
        print(f"  Resume embeddings: {stats['resume_embedding']['valid_count']}")
        print(f"  Average job embedding norm: {stats['job_embeddings']['mean_norm']:.4f}")
        
        # Export report
        report_file = generator.export_embeddings_report()
        print(f"\n📄 Exported embedding report to: {report_file}")
        
    except Exception as e:
        print(f"❌ Error in complete pipeline: {e}")

def demonstrate_stage4_similarity_and_top_jobs():
    """Demonstrate Stage 4: Similarity calculation and top job selection."""
    print("\n🏆 Stage 4: Similarity Calculation and Top Job Selection")
    print("=" * 60)
    
    # Check for API key and real embeddings
    api_key = os.getenv('OPENAI_API_KEY')
    generator = None
    try:
        generator = EmbeddingGenerator(api_key=api_key, model="text-embedding-3-small")
    except Exception as e:
        print(f"⚠️  Could not initialize EmbeddingGenerator: {e}")
        print("   Make sure you have run Stage 3 with a real API key and embeddings exist.")
        return
    
    # Get resume embedding
    resume_data = generator.manager.get_resume_embedding()
    if not resume_data:
        print("⚠️  No resume embedding found. Run Stage 3 with a real resume.")
        return
    resume_embedding_id, resume_embedding_data = resume_data
    resume_embedding = resume_embedding_data.get('embedding', [])
    if not resume_embedding:
        print("⚠️  Resume embedding is empty.")
        return
    
    # Get all job embeddings
    job_embeddings_data = generator.manager.get_job_embeddings()
    if not job_embeddings_data:
        print("⚠️  No job embeddings found. Run Stage 3 with real job data.")
        return
    
    # Calculate cosine similarity for each job
    results = []
    for embedding_id, embedding_data in job_embeddings_data:
        job_embedding = embedding_data.get('embedding', [])
        if not job_embedding:
            continue
        score = generator.calculator.cosine_similarity(resume_embedding, job_embedding)
        results.append({
            'embedding_id': embedding_id,
            'job_title': embedding_data.get('metadata', {}).get('job_title', ''),
            'company_name': embedding_data.get('metadata', {}).get('company_name', ''),
            'location': embedding_data.get('metadata', {}).get('location', ''),
            'similarity_score': score
        })
    
    # Sort by similarity descending
    results.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    # Display top 10
    print(f"\nTop 10 Most Similar Jobs to Resume:")
    print("-" * 60)
    for i, job in enumerate(results[:10], 1):
        print(f"{i:2d}. {job['job_title']} at {job['company_name']}")
        print(f"     Location: {job['location']}")
        print(f"     Similarity: {job['similarity_score']:.4f}")
        print("-")
    if not results:
        print("No job similarities could be calculated.")
    print("\n🏁 Stage 4 complete!")

def main():
    """Main function to demonstrate Stage 3 embedding generation and Stage 4 similarity."""
    print("🚀 Stage 3: Embedding Generation Demonstration")
    print("=" * 60)
    
    try:
        # Demonstrate individual components
        generator = demonstrate_embedding_generator()
        calculator = demonstrate_similarity_calculator()
        manager = demonstrate_embedding_manager()
        embedder = demonstrate_openai_embedder()
        
        # Demonstrate complete pipeline
        demonstrate_complete_pipeline()
        
        # Stage 4: Similarity and Top Job Selection
        demonstrate_stage4_similarity_and_top_jobs()
        
        print("\n" + "=" * 60)
        print("✅ Stage 3 Embedding Generation Complete!")
        print("\nThe system now includes:")
        print("✅ OpenAI API integration with rate limiting and error handling")
        print("✅ Batch embedding generation for efficiency")
        print("✅ Comprehensive embedding storage and management")
        print("✅ Multiple similarity calculation methods")
        print("✅ Job-resume similarity matching")
        print("✅ Usage tracking and cost monitoring")
        print("✅ Comprehensive reporting and statistics")
        print("✅ Top-N job selection based on cosine similarity (Stage 4)")
        
        print(f"\n📁 Generated files:")
        print(f"   - data/embeddings/ (embedding storage)")
        print(f"   - embedding_report_*.json (comprehensive reports)")
        
        print("\n🎯 Ready for Stage 5: User Feedback Loop!")
        
        # API key instructions
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("\n🔑 To test with real API calls:")
            print("   1. Get an OpenAI API key from https://platform.openai.com/")
            print("   2. Set environment variable: export OPENAI_API_KEY='your-key-here'")
            print("   3. Run this script again for full functionality")
        
    except Exception as e:
        logger.error(f"Error in embedding demonstration: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
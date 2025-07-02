#!/usr/bin/env python3
"""
Standalone Adzuna API Test - Free job data for St. Louis
No complex imports, just direct API testing.
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import List, Dict, Any

class AdzunaAPI:
    """Simple Adzuna API client."""
    
    def __init__(self, app_id: str = "demo", app_key: str = "demo"):
        self.app_id = app_id
        self.app_key = app_key
        self.base_url = "https://api.adzuna.com/v1/api/jobs/us/search"
        
    def search_jobs(self, keywords: str, location: str = "St. Louis, MO", max_jobs: int = 20) -> List[Dict[str, Any]]:
        """Search for jobs using Adzuna API."""
        jobs = []
        page = 1
        
        try:
            while len(jobs) < max_jobs:
                params = {
                    'app_id': self.app_id,
                    'app_key': self.app_key,
                    'results_per_page': min(20, max_jobs - len(jobs)),
                    'what': keywords,
                    'where': location,
                    'page': page
                }
                
                print(f"  Searching page {page} for '{keywords}'...")
                
                response = requests.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                page_jobs = data.get('results', [])
                
                if not page_jobs:
                    print(f"  No more jobs found on page {page}")
                    break
                
                for job_data in page_jobs:
                    if len(jobs) >= max_jobs:
                        break
                    
                    processed_job = self._process_job(job_data)
                    if processed_job:
                        jobs.append(processed_job)
                
                page += 1
                time.sleep(1)  # Rate limiting
                
                if page > 5:  # Safety limit
                    break
            
            return jobs
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ API request error: {e}")
            return jobs
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return jobs
    
    def _process_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw job data from API."""
        try:
            # Extract basic info
            title = job_data.get('title', '')
            company = job_data.get('company', {}).get('display_name', '')
            location = job_data.get('location', {}).get('display_name', '')
            description = job_data.get('description', '')
            
            # Clean description
            if description:
                import re
                description = re.sub(r'<[^>]+>', '', description)
                description = description.replace('&nbsp;', ' ').strip()
            
            # Extract salary
            salary_min = job_data.get('salary_min', 0)
            salary_max = job_data.get('salary_max', 0)
            if salary_min and salary_max:
                salary = f"${salary_min:,} - ${salary_max:,}"
            elif salary_min:
                salary = f"${salary_min:,}+"
            else:
                salary = "Not specified"
            
            # Extract skills
            skills = self._extract_skills(description)
            
            return {
                'job_title': title,
                'company_name': company,
                'location': location,
                'job_description': description[:500] + "..." if len(description) > 500 else description,
                'required_skills': ', '.join(skills),
                'salary_range': salary,
                'posted_date': job_data.get('created', ''),
                'job_url': job_data.get('redirect_url', ''),
                'source_website': 'Adzuna',
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"  Error processing job: {e}")
            return None
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract skills from job description."""
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
        
        return found_skills[:8]  # Limit to top 8 skills

def main():
    """Main function to test Adzuna API."""
    print("🚀 Adzuna API Test for St. Louis Jobs")
    print("=" * 50)
    print("Testing free Adzuna API to get real job data from St. Louis")
    print()
    
    # Initialize API client
    api = AdzunaAPI()
    
    # Search terms for St. Louis tech jobs
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
        
        jobs = api.search_jobs(term, "St. Louis, MO", max_jobs=10)
        
        print(f"✅ Found {len(jobs)} jobs for '{term}'")
        
        # Show sample jobs
        for i, job in enumerate(jobs[:3]):
            print(f"   {i+1}. {job.get('job_title', 'N/A')}")
            print(f"      Company: {job.get('company_name', 'N/A')}")
            print(f"      Location: {job.get('location', 'N/A')}")
            print(f"      Salary: {job.get('salary_range', 'N/A')}")
            print(f"      Skills: {job.get('required_skills', 'N/A')}")
            print()
        
        all_jobs.extend(jobs)
    
    # Save results
    if all_jobs:
        print(f"\n📊 Total jobs found: {len(all_jobs)}")
        
        # Remove duplicates based on job title and company
        unique_jobs = []
        seen = set()
        
        for job in all_jobs:
            key = f"{job.get('job_title', '')}-{job.get('company_name', '')}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        print(f"✅ Unique jobs after deduplication: {len(unique_jobs)}")
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"st_louis_adzuna_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs("data/raw", exist_ok=True)
        filepath = os.path.join("data/raw", filename)
        
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
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {filepath}")
        
        # Show summary
        stats = results['statistics']
        print(f"\n📈 Summary:")
        print(f"   Total jobs: {stats['total_jobs']}")
        print(f"   Unique companies: {stats['unique_companies']}")
        print(f"   Search terms: {', '.join(search_terms)}")
        
        # Show sample job titles
        print(f"\n📋 Sample Job Titles:")
        for i, job in enumerate(unique_jobs[:5]):
            print(f"   {i+1}. {job.get('job_title', 'N/A')}")
        
        print(f"\n✅ API test completed successfully!")
        print(f"🔗 Sign up at https://developer.adzuna.com/ for full access")
        
    else:
        print("❌ No jobs found")
        print("🔗 Try signing up at https://developer.adzuna.com/ for better access")

if __name__ == "__main__":
    main() 
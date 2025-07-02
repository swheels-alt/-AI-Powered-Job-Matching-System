#!/usr/bin/env python3
"""
Debug script to test file loading logic
"""

import os
import json
from datetime import datetime

def debug_load_st_louis_jobs():
    """Debug the file loading logic."""
    print("🔍 Debugging File Loading Logic")
    print("=" * 50)
    
    # Find the most recent St. Louis job file
    raw_dir = "data/raw"
    print(f"📁 Looking in directory: {raw_dir}")
    
    if not os.path.exists(raw_dir):
        print(f"❌ Directory {raw_dir} does not exist!")
        return None
    
    st_louis_files = [f for f in os.listdir(raw_dir) if f.startswith("st_louis_") and f.endswith(".json")]
    print(f"📋 Found {len(st_louis_files)} St. Louis files:")
    for f in st_louis_files:
        filepath = os.path.join(raw_dir, f)
        ctime = os.path.getctime(filepath)
        ctime_str = datetime.fromtimestamp(ctime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"   - {f} (created: {ctime_str})")
    
    if not st_louis_files:
        print("❌ No St. Louis job files found.")
        return None
    
    # Prioritize enhanced datasets (they have more jobs)
    enhanced_files = [f for f in st_louis_files if "enhanced" in f]
    print(f"\n🔍 Enhanced files found: {len(enhanced_files)}")
    for f in enhanced_files:
        print(f"   - {f}")
    
    if enhanced_files:
        # Get the most recent enhanced file
        latest_file = max(enhanced_files, key=lambda x: os.path.getctime(os.path.join(raw_dir, x)))
        filepath = os.path.join(raw_dir, latest_file)
        print(f"\n✅ Selected enhanced file: {filepath}")
    else:
        # Fall back to regular files
        latest_file = max(st_louis_files, key=lambda x: os.path.getctime(os.path.join(raw_dir, x)))
        filepath = os.path.join(raw_dir, latest_file)
        print(f"\n⚠️  No enhanced files found, using: {filepath}")
    
    # Load the file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        jobs = data['jobs']
        print(f"📊 Successfully loaded {len(jobs)} jobs from dataset")
        
        # Show first few job titles
        print("\n📋 Sample job titles:")
        for i, job in enumerate(jobs[:5]):
            print(f"   {i+1}. {job.get('job_title', 'N/A')}")
        
        return jobs
        
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None

if __name__ == "__main__":
    debug_load_st_louis_jobs() 
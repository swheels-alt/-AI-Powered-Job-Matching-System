# 🚀 AI-Powered Job Matching System - Terminal Guide

## Quick Start

```bash
# Clone and setup
git clone https://github.com/swheels-alt/-AI-Powered-Job-Matching-System.git
cd -AI-Powered-Job-Matching-System
pip install -r requirements.txt

# Run with your resume (RECOMMENDED)
python run_with_my_resume.py
```

## Main Commands

### 🎯 Use Your Resume (Best Option)
```bash
python run_with_my_resume.py
```
- Paste your resume when prompted
- Type 'END' when finished
- Get top 10 personalized job matches

### 📊 Standard Pipeline
```bash
python run_st_louis_pipeline.py
```
- Uses sample resume
- Shows top 10 matches for St. Louis

### 🔄 Generate Job Data
```bash
python free_job_api_test.py
```
- Creates fresh St. Louis job data
- Run this first if you get "no job files found"

## File Structure
```
data/
├── raw/                    # Job data files
└── processed/              # Reports and results
src/                        # Source code
run_with_my_resume.py       # 🎯 MAIN SCRIPT
requirements.txt            # Dependencies
```

## Complete Workflow
```bash
# 1. Generate job data (first time only)
python free_job_api_test.py

# 2. Run with your resume
python run_with_my_resume.py
# [Paste your resume]
# [Type 'END']
```

## Troubleshooting
- **No job files**: Run `python free_job_api_test.py` first
- **Import errors**: Run `pip install -r requirements.txt`
- **Permission errors**: Run `chmod +x *.py`

## Results
- **Terminal**: Shows top 10 matches immediately
- **Files**: Check `data/processed/` for detailed reports
- **Match scores**: 1.0000 = perfect, 0.9000+ = excellent

## Customization
- **Change city**: Edit `src/config/settings.py`
- **Add API keys**: Set `export OPENAI_API_KEY='your-key'`
- **Add job sources**: Edit `free_job_api_test.py`

**Ready? Run: `python run_with_my_resume.py`** 
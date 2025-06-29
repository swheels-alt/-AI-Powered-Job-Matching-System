# AI-Powered Job Matching System

An intelligent system that scrapes job postings, embeds them using AI models, embeds user resumes, and identifies the top 10 most similar job postings.

## Project Overview

This system consists of multiple stages:
- **Stage 1**: Data Acquisition (Job Postings) - ✅ COMPLETED
- **Stage 2**: Data Processing and Embedding
- **Stage 3**: Resume Processing and Matching
- **Stage 4**: User Interface and Results Display

## Stage 1: Data Acquisition Strategy

### Approach: Web Scraping with Ethical Considerations

We've implemented a comprehensive web scraping solution that respects website policies and includes proper error handling.

#### Target Websites:
- **Indeed**: Primary source for job postings
- **LinkedIn**: Secondary source for professional positions
- **Glassdoor**: Additional source for company insights

#### Ethical Considerations:
- ✅ Respects robots.txt files
- ✅ Implements rate limiting (2-5 second delays between requests)
- ✅ Includes user-agent headers to identify the scraper
- ✅ Handles errors gracefully without overwhelming servers
- ✅ Focuses on publicly available job posting data

#### Data Fields Collected:
- Job Title
- Company Name
- Location
- Job Description
- Required Skills
- Experience Level
- Salary Range (when available)
- Posted Date
- Job URL

### Technical Implementation:
- **BeautifulSoup4**: HTML parsing
- **Requests**: HTTP requests with proper headers
- **Selenium**: For dynamic content (when needed)
- **Pandas**: Data manipulation and CSV export
- **JSON**: Structured data storage

### Usage:
```bash
# Install dependencies
pip install -r requirements.txt

# Run the job scraper
python src/scrapers/job_scraper.py

# Run with specific filters
python src/scrapers/job_scraper.py --location "St. Louis" --keywords "computer science"
```

## Project Structure
```
JobFinder_Project/
├── src/
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── job_scraper.py
│   │   ├── indeed_scraper.py
│   │   ├── linkedin_scraper.py
│   │   └── glassdoor_scraper.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── data_processor.py
│   │   └── error_handler.py
│   └── config/
│       ├── __init__.py
│       └── settings.py
├── data/
│   ├── raw/
│   └── processed/
├── tests/
├── requirements.txt
└── README.md
```

## Installation and Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the scraper: `python src/scrapers/job_scraper.py`

## Output

Stage 1 produces:
- CSV files with job postings data
- JSON files for structured data storage
- Comprehensive logging of the scraping process
- Error reports for failed requests

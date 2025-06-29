# AI-Powered Job Matching System

An intelligent system that matches job seekers with relevant job postings using AI and machine learning techniques.

## Project Overview

This system implements a comprehensive job matching pipeline that:
1. **Acquires** job posting data from multiple sources
2. **Preprocesses** and cleans the data for optimal embedding generation
3. **Generates** embeddings for semantic similarity matching
4. **Matches** job seekers with relevant opportunities
5. **Recommends** personalized job suggestions

## Project Status

- ✅ **Stage 1: Data Acquisition** - Complete
- ✅ **Stage 2: Data Preprocessing** - Complete
- 🔄 **Stage 3: Embedding Generation** - Pending
- ⏳ **Stage 4: Matching Algorithm** - Pending
- ⏳ **Stage 5: Recommendation System** - Pending

## Stage 1: Data Acquisition ✅

### Overview
Comprehensive data acquisition system that ethically scrapes job postings from multiple sources including Indeed and LinkedIn.

### Features
- **Multi-source scraping**: Indeed and LinkedIn integration
- **Ethical scraping**: Rate limiting, user agents, and respectful crawling
- **Robust error handling**: Comprehensive error recovery and logging
- **Data validation**: Quality checks and duplicate removal
- **Flexible output**: JSON and CSV formats
- **Production ready**: Configurable settings and monitoring

### Key Components
- `src/scrapers/` - Scraping modules for different job sites
- `src/utils/` - Data processing and error handling utilities
- `src/config/` - Configuration management
- `data/raw/` - Raw scraped data storage

### Usage
```bash
# Run the scraper
python demo_scraper.py

# Test the system
python test_scraper.py
```

## Stage 2: Data Preprocessing ✅

### Overview
Comprehensive preprocessing pipeline that cleans and prepares job data and resume text for embedding generation.

### Features
- **Text Cleaning**: HTML removal, special character handling, whitespace normalization
- **Data Normalization**: Location, job title, and experience level standardization
- **Skill Extraction**: Automated skill identification from job descriptions
- **Resume Parsing**: Section extraction and contact information parsing
- **Missing Data Handling**: Multiple strategies for incomplete data
- **Embedding Preparation**: Text preparation optimized for embedding models
- **Quality Validation**: Data quality checks and reporting

### Key Components

#### Text Cleaning (`src/preprocessing/text_cleaner.py`)
- HTML tag removal and entity decoding
- Special character handling with punctuation preservation
- Location normalization (e.g., "St. Louis, MO" → "Saint Louis, MISSOURI")
- Job title normalization (e.g., "Sr. Software Eng." → "Senior Software Engineer")
- Skill extraction using keyword matching
- Stop word removal and lemmatization
- Embedding-optimized text preparation

#### Data Preprocessing (`src/preprocessing/data_preprocessor.py`)
- Comprehensive job data preprocessing pipeline
- Missing data handling strategies (fill_na, remove, interpolate)
- Experience level categorization (junior, mid-level, senior)
- Salary range normalization
- Data validation and quality checks
- Preprocessing statistics and reporting

#### Resume Parsing (`src/preprocessing/resume_parser.py`)
- Section-based resume parsing (experience, education, skills, projects)
- Contact information extraction (email, phone, LinkedIn, GitHub)
- Skill extraction from all resume sections
- Experience and education detail parsing
- Resume summary generation

#### Embedding Preparation (`src/preprocessing/embedding_preparer.py`)
- Coordinated preprocessing for embedding generation
- Batch processing of jobs and resume data
- Embedding text creation optimized for similarity matching
- Data validation and quality assurance
- Comprehensive reporting and statistics

### Preprocessing Pipeline

1. **Text Cleaning**
   - Remove HTML tags and decode entities
   - Normalize whitespace and special characters
   - Convert to lowercase for consistency

2. **Data Normalization**
   - Standardize location formats
   - Normalize job titles and abbreviations
   - Categorize experience levels

3. **Skill Extraction**
   - Extract skills from job descriptions
   - Parse comma-separated skill lists
   - Remove duplicates and normalize

4. **Missing Data Handling**
   - Fill missing fields with "N/A"
   - Remove incomplete entries (optional)
   - Interpolate based on similar jobs (optional)

5. **Embedding Preparation**
   - Create optimized text for embedding models
   - Combine relevant fields (title, company, description, skills)
   - Apply optional preprocessing (stop words, lemmatization)

### Usage

#### Basic Preprocessing
```python
from src.preprocessing.embedding_preparer import EmbeddingPreparer

# Initialize preparer
preparer = EmbeddingPreparer()

# Prepare jobs for embedding
prepared_jobs = preparer.prepare_jobs_for_embedding(jobs_data)

# Prepare resume for embedding
prepared_resume = preparer.prepare_resume_for_embedding(resume_text)
```

#### Complete Pipeline
```python
# Create embedding batch with both jobs and resume
embedding_batch = preparer.create_embedding_batch(
    jobs_data, 
    resume_text,
    preprocessing_config={
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

# Save the batch
filepath = preparer.save_embedding_batch(embedding_batch)
```

#### Demonstration
```bash
# Run the complete preprocessing demonstration
python preprocess_data.py
```

### Output Files
- `data/processed/embedding_batch_*.json` - Complete embedding-ready data
- `data/processed/preprocessed_jobs_*.json` - Preprocessed job data

### Preprocessing Statistics
The system provides comprehensive statistics including:
- Original vs preprocessed job counts
- Skills extraction metrics
- Experience level distribution
- Location distribution
- Data quality metrics
- Processing time and validation results

## Stage 3: Embedding Generation 🔄

### Planned Features
- Integration with embedding models (OpenAI, Sentence Transformers)
- Batch embedding generation
- Embedding storage and management
- Similarity calculation utilities
- Performance optimization

## Stage 4: Matching Algorithm ⏳

### Planned Features
- Semantic similarity matching
- Skill-based matching
- Experience level filtering
- Location-based filtering
- Customizable matching criteria

## Stage 5: Recommendation System ⏳

### Planned Features
- Personalized job recommendations
- Ranking algorithms
- User preference learning
- Feedback integration
- Recommendation explanations

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd JobFinder_Project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up configuration:
```bash
# Copy and modify configuration files as needed
cp src/config/settings.py.example src/config/settings.py
```

## Project Structure

```
JobFinder_Project/
├── data/
│   ├── raw/                 # Raw scraped data
│   └── processed/           # Preprocessed data
├── src/
│   ├── config/             # Configuration management
│   ├── scrapers/           # Data acquisition modules
│   ├── preprocessing/      # Data preprocessing modules
│   └── utils/              # Utility functions
├── tests/                  # Test files
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── demo_scraper.py        # Data acquisition demo
├── preprocess_data.py     # Preprocessing demo
└── test_scraper.py        # System testing
```

## Configuration

The system uses a centralized configuration system in `src/config/settings.py`:

- **Scraping settings**: URLs, headers, rate limits
- **Preprocessing settings**: Text cleaning options, skill extraction
- **Output settings**: File formats, storage locations
- **Logging settings**: Log levels and output formats

## Usage Examples

### Data Acquisition
```python
from src.scrapers.job_scraper import JobScraper

scraper = JobScraper()
jobs = scraper.scrape_jobs(
    location="St. Louis, MO",
    keywords="computer science",
    max_jobs=100
)
```

### Data Preprocessing
```python
from src.preprocessing.embedding_preparer import EmbeddingPreparer

preparer = EmbeddingPreparer()
embedding_batch = preparer.create_embedding_batch(jobs_data, resume_text)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python 3.13
- Uses BeautifulSoup for HTML parsing
- Selenium for dynamic content scraping
- Comprehensive error handling and logging
- Ethical scraping practices

---

**Current Status**: Stage 2 (Data Preprocessing) completed successfully. The system now includes comprehensive text cleaning, data normalization, skill extraction, resume parsing, and embedding preparation capabilities. Ready to proceed to Stage 3: Embedding Generation.

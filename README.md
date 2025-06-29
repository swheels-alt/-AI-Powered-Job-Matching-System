# AI-Powered Job Matching System

## Overview
This project is an end-to-end AI-powered job matching system that scrapes job postings, preprocesses and cleans the data, generates embeddings for both jobs and resumes, and matches candidates to jobs using state-of-the-art similarity techniques.

---

## Stages & Features

### 1. Data Acquisition
- **Sources:** Indeed, LinkedIn (ethical scraping, configurable by location/keywords)
- **Output:** Raw job data in JSON/CSV
- **Challenges:** Rate limits, anti-bot measures, data consistency, ethical/legal compliance

### 2. Preprocessing
- **Text Cleaning:** HTML removal, normalization, lemmatization, stop word removal
- **Skill Extraction:** From job descriptions and resumes
- **Data Validation:** Handling missing data, salary normalization, experience categorization
- **Resume Parsing:** Section extraction, contact info, skills, experience, education, projects
- **Output:** Cleaned, normalized, embedding-ready data

### 3. Embedding Generation
- **Models:**
  - OpenAI `text-embedding-3-small` (default, can be swapped for `text-embedding-3-large` or Gemini)
- **API Usage:** Batching, rate limiting, cost tracking, error handling
- **Output:** Embeddings for all jobs and the resume, stored with metadata

### 4. Similarity Calculation & Top Job Selection
- **Metric:** Cosine similarity (numpy, scipy)
- **Ranking:** All jobs ranked by similarity to the resume
- **Output:** Top 10 jobs with job title, company, location, and similarity score

### 5. Reporting & Analysis
- **Comprehensive Report:**
  - Data acquisition method and challenges
  - Preprocessing steps
  - Embedding model(s) used and rationale
  - Similarity calculation method
  - Top 10 job matches with scores
  - Analysis of results, strengths/weaknesses, and future work
- **Repository:**
  - All code, sample data (anonymized), and instructions included

---

## How to Run
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY='your-key-here'
   ```
3. **Run the embedding and matching pipeline:**
   ```bash
   python generate_embeddings.py
   ```
4. **Review the output:**
   - Embeddings and reports in `data/embeddings/` and as `embedding_report_*.json`
   - Top 10 job matches printed in the console
   - Comprehensive report in `STAGE5_REPORT.md`

---

## Strengths & Weaknesses
**Strengths:**
- Modular, extensible, and well-documented code
- Supports multiple embedding models (OpenAI, Gemini)
- Handles real-world data issues (missing data, noise, etc.)
- Batch processing and cost tracking for API usage
- Clear reporting and statistics

**Weaknesses:**
- Dependent on the quality of scraped data
- Embedding models may not capture all nuances of job fit
- Resume parsing is heuristic and may miss some information
- API costs for large-scale use

## Future Work
- Incorporate more advanced matching (e.g., neural ranking, LLMs)
- Improve resume parsing with NLP models
- Add user feedback loop for iterative improvement
- Support more job boards and resume formats
- Add web UI for interactive job search

---

## License
MIT
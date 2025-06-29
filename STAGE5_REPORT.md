# Stage 5 Report: AI-Powered Job Matching System

## 1. Data Acquisition Method & Challenges
- **Sources:** Indeed and LinkedIn, using ethical scraping with configurable location and keyword filters.
- **Method:** Selenium and BeautifulSoup for scraping, with user-agent rotation and delays to avoid detection.
- **Challenges:**
  - Rate limits and anti-bot measures (CAPTCHAs, IP blocks)
  - Data inconsistency and missing fields
  - Ensuring compliance with terms of service and privacy/ethics

## 2. Preprocessing Steps
- **Text Cleaning:** HTML removal, normalization, lowercasing, special character handling
- **Skill Extraction:** Regex and keyword-based extraction from job/resume text
- **Stop Word Removal & Lemmatization:** Optional, configurable
- **Data Validation:** Handling missing data, salary normalization, experience level categorization
- **Resume Parsing:** Section extraction (contact, skills, experience, education, projects)
- **Output:** Cleaned, normalized, and embedding-ready data

## 3. Embedding Model(s) Used & Rationale
- **Primary Model:** OpenAI `text-embedding-3-small`
  - Chosen for its strong performance, API support, and cost-effectiveness
- **Alternative Model (optional):** OpenAI `text-embedding-3-large` or Gemini (can be swapped in code)
- **Batching:** Used for efficiency and cost savings
- **API Handling:** Rate limiting, exponential backoff, and cost tracking implemented

## 4. Similarity Calculation
- **Metric:** Cosine similarity (using numpy and scipy)
- **Process:**
  - Resume embedding is compared to each job embedding
  - All jobs are ranked by similarity score
  - Top 10 jobs are selected and displayed

## 5. Top 10 Job Postings (Example Output)
| Rank | Job Title              | Company           | Location         | Similarity Score |
|------|------------------------|-------------------|------------------|-----------------|
| 1    | Software Engineer      | TechCorp Inc.     | Saint Louis, MO  | 0.9123          |
| 2    | Senior Python Developer| DataSolutions LLC | Saint Louis, MO  | 0.8991          |
| 3    | Frontend Developer     | WebTech Solutions | Saint Louis, MO  | 0.8722          |
| ...  | ...                    | ...               | ...              | ...             |

*Note: Actual scores and jobs will depend on your data and API key.*

## 6. Analysis of Results
- **Do the top jobs make sense?**
  - In most cases, the top jobs are highly relevant to the resume, especially when skills and experience align.
  - Some jobs may appear due to keyword overlap rather than true fit (limitation of embedding models).
- **Strengths:**
  - Fast, scalable, and model-agnostic
  - Handles noisy, real-world data
  - Easily extensible to new models or data sources
- **Weaknesses:**
  - Embeddings may miss subtle fit factors (e.g., culture, soft skills)
  - Resume parsing is heuristic and may miss some information
  - Dependent on the quality and recency of scraped data
- **Comparison of Two Models (if run):**
  - `text-embedding-3-large` may provide slightly better semantic matching but at higher cost and slower speed.
  - Gemini models (if used) can be swapped in with minor code changes for experimentation.

## 7. Possible Improvements & Future Work
- Use more advanced matching (e.g., neural ranking, LLMs, hybrid models)
- Improve resume parsing with NLP models
- Add user feedback loop for iterative improvement
- Support more job boards and resume formats
- Add a web UI for interactive job search and feedback
- Experiment with more filtering and ranking options (e.g., location, salary, company type)

## 8. Repository Organization
- **Code:** All source code in `src/` and main scripts in root
- **Data:** Anonymized sample data in `data/`
- **Reports:** This report and embedding reports in project root
- **README:** Full instructions and project overview

---

*Prepared by: [Your Name]*
*Date: [YYYY-MM-DD]* 
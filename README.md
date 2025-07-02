# AI-Powered Job Matching System

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/swheels-alt/-AI-Powered-Job-Matching-System.git
cd -AI-Powered-Job-Matching-System

# Run setup (optional)
./setup.sh

# Use with your resume (RECOMMENDED)
python run_with_my_resume.py
```

## 🎯 Main Features

### **Personalized Job Matching**
- **Input your resume** and get top 10 job matches
- **Real St. Louis tech jobs** from major companies
- **AI-powered matching** using similarity algorithms
- **Detailed reports** with match scores and application links

### **Companies Included**
- Boeing, Centene, Express Scripts, World Wide Technology
- Ameren, Anheuser-Busch, Mastercard, Edward Jones
- And more St. Louis tech companies

## 📋 How to Use

### **1. Use Your Resume (Best Option)**
```bash
python run_with_my_resume.py
```
- Paste your resume when prompted
- Type 'END' when finished
- Get personalized top 10 matches

### **2. Standard Pipeline**
```bash
python run_st_louis_pipeline.py
```
- Uses sample resume
- Good for testing the system

### **3. Generate Job Data**
```bash
python free_job_api_test.py
```
- Creates fresh St. Louis job data
- Run first if you get "no job files found"

## 📊 Example Output

```
🏆 TOP 10 JOB MATCHES FOR YOUR RESUME
============================================================

1. Software Engineer at Boeing
   Location: Saint Louis, MO
   Salary: $80,000 - $120,000
   Skills: java, python, aerospace, real-time systems, embedded software
   Match Score: 0.9876
   Apply: https://jobs.boeing.com/software-engineer

2. Python Developer at Centene Corporation
   Location: Saint Louis, MO
   Salary: $75,000 - $110,000
   Skills: python, django, postgresql, healthcare, hipaa
   Match Score: 0.9543
   Apply: https://careers.centene.com/python-developer
```

## 🔧 System Architecture

### **Stages**
1. **Data Acquisition** - Collect job postings from St. Louis
2. **Preprocessing** - Clean and normalize job data and resume
3. **Embedding Generation** - Create AI embeddings for matching
4. **Similarity Calculation** - Rank jobs by match score
5. **Reporting** - Generate top 10 matches with details

### **Technologies**
- **Python 3.8+** - Core language
- **OpenAI Embeddings** - AI-powered matching (optional)
- **Cosine Similarity** - Job-resume matching algorithm
- **JSON/CSV** - Data storage and reporting

## 📁 Project Structure

```
JobFinder_Project/
├── data/
│   ├── raw/                    # Job data files
│   └── processed/              # Reports and results
├── src/
│   ├── scrapers/               # Job scraping modules
│   ├── preprocessing/          # Data cleaning and preparation
│   ├── embeddings/             # AI embedding generation
│   └── utils/                  # Utility functions
├── run_with_my_resume.py       # 🎯 MAIN SCRIPT
├── run_st_louis_pipeline.py    # Standard pipeline
├── free_job_api_test.py        # Generate job data
├── setup.sh                    # Setup script
├── TERMINAL_GUIDE.md           # Detailed usage guide
└── requirements.txt            # Dependencies
```

## 🎯 Complete Workflow

```bash
# 1. Setup (first time only)
git clone https://github.com/swheels-alt/-AI-Powered-Job-Matching-System.git
cd -AI-Powered-Job-Matching-System
pip install -r requirements.txt

# 2. Generate job data (first time only)
python free_job_api_test.py

# 3. Run with your resume
python run_with_my_resume.py
# [Paste your resume when prompted]
# [Type 'END' when finished]
```

## 🔧 Customization

### **Change Location**
Edit `src/config/settings.py`:
```python
DEFAULT_LOCATION = "Your City, State"  # Change from "St. Louis, MO"
```

### **Add API Keys**
For real embedding generation:
```bash
export OPENAI_API_KEY='your-openai-key-here'
```

### **Add Job Sources**
- Edit `free_job_api_test.py` to add more job sources
- Add your own job data to `data/raw/`

## 🚨 Troubleshooting

- **No job files**: Run `python free_job_api_test.py` first
- **Import errors**: Run `pip install -r requirements.txt`
- **Permission errors**: Run `chmod +x *.py`

## 📈 Results

- **Terminal**: Shows top 10 matches immediately
- **Files**: Check `data/processed/` for detailed reports
- **Match scores**: 1.0000 = perfect, 0.9000+ = excellent

## 🚀 Next Steps

1. **Try with your resume**: `python run_with_my_resume.py`
2. **Customize for your city**: Edit `src/config/settings.py`
3. **Add real API keys**: For production use
4. **Extend functionality**: Add more job sources or features

---

**🎯 Ready to get started? Run:**
```bash
python run_with_my_resume.py
```

**📖 For detailed usage, see [TERMINAL_GUIDE.md](TERMINAL_GUIDE.md)**


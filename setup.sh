#!/bin/bash

echo "🚀 AI-Powered Job Matching System Setup"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x *.py

# Generate initial job data
echo "📊 Generating initial job data..."
python free_job_api_test.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 To get started, run:"
echo "   python run_with_my_resume.py"
echo ""
echo "📖 For more info, see TERMINAL_GUIDE.md" 
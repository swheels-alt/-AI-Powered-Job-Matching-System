"""
Text cleaning utilities for preprocessing job data and resume text.
"""

import re
import string
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import unquote
import html

logger = logging.getLogger(__name__)

class TextCleaner:
    """Handles text cleaning and normalization for job data and resumes."""
    
    def __init__(self):
        # Common HTML entities and their replacements
        self.html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&nbsp;': ' ',
            '&copy;': '©',
            '&reg;': '®',
            '&trade;': '™'
        }
        
        # Common abbreviations and their full forms
        self.location_abbreviations = {
            'st.': 'saint',
            'mo.': 'missouri',
            'ca.': 'california',
            'ny.': 'new york',
            'tx.': 'texas',
            'fl.': 'florida',
            'il.': 'illinois',
            'pa.': 'pennsylvania',
            'oh.': 'ohio',
            'mi.': 'michigan',
            'ga.': 'georgia',
            'nc.': 'north carolina',
            'va.': 'virginia',
            'wa.': 'washington',
            'or.': 'oregon',
            'az.': 'arizona',
            'co.': 'colorado',
            'ut.': 'utah',
            'nv.': 'nevada',
            'nm.': 'new mexico',
            'ok.': 'oklahoma',
            'ar.': 'arkansas',
            'la.': 'louisiana',
            'ms.': 'mississippi',
            'al.': 'alabama',
            'tn.': 'tennessee',
            'ky.': 'kentucky',
            'in.': 'indiana',
            'wi.': 'wisconsin',
            'mn.': 'minnesota',
            'ia.': 'iowa',
            'ne.': 'nebraska',
            'ks.': 'kansas',
            'nd.': 'north dakota',
            'sd.': 'south dakota',
            'mt.': 'montana',
            'wy.': 'wyoming',
            'id.': 'idaho',
            'ak.': 'alaska',
            'hi.': 'hawaii',
            'me.': 'maine',
            'nh.': 'new hampshire',
            'vt.': 'vermont',
            'ma.': 'massachusetts',
            'ri.': 'rhode island',
            'ct.': 'connecticut',
            'nj.': 'new jersey',
            'de.': 'delaware',
            'md.': 'maryland',
            'dc.': 'district of columbia',
            'wv.': 'west virginia',
            'sc.': 'south carolina'
        }
        
        # Common job title abbreviations
        self.job_abbreviations = {
            'sr.': 'senior',
            'jr.': 'junior',
            'eng.': 'engineer',
            'dev.': 'developer',
            'mgr.': 'manager',
            'dir.': 'director',
            'vp.': 'vice president',
            'ceo.': 'chief executive officer',
            'cto.': 'chief technology officer',
            'cfo.': 'chief financial officer',
            'coo.': 'chief operating officer',
            'pm.': 'project manager',
            'po.': 'product owner',
            'ba.': 'business analyst',
            'qa.': 'quality assurance',
            'ui.': 'user interface',
            'ux.': 'user experience',
            'api.': 'application programming interface',
            'sdk.': 'software development kit',
            'ui/ux.': 'user interface/user experience'
        }
        
        # Common stop words (can be customized)
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
            'had', 'what', 'said', 'each', 'which', 'she', 'do', 'how', 'their',
            'if', 'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some',
            'her', 'would', 'make', 'like', 'into', 'him', 'time', 'two',
            'more', 'go', 'no', 'way', 'could', 'my', 'than', 'first', 'been',
            'call', 'who', 'its', 'now', 'find', 'long', 'down', 'day', 'did',
            'get', 'come', 'made', 'may', 'part', 'over', 'new', 'sound',
            'take', 'only', 'little', 'work', 'know', 'place', 'year', 'live',
            'me', 'back', 'give', 'most', 'very', 'after', 'thing', 'our',
            'just', 'name', 'good', 'sentence', 'man', 'think', 'say', 'great',
            'where', 'help', 'through', 'much', 'before', 'line', 'right',
            'too', 'mean', 'old', 'any', 'same', 'tell', 'boy', 'follow',
            'came', 'want', 'show', 'also', 'around', 'form', 'three',
            'small', 'set', 'put', 'end', 'does', 'another', 'well',
            'large', 'must', 'big', 'even', 'such', 'because', 'turn',
            'here', 'why', 'ask', 'went', 'men', 'read', 'need', 'land',
            'different', 'home', 'us', 'move', 'try', 'kind', 'hand',
            'picture', 'again', 'change', 'off', 'play', 'spell', 'air',
            'away', 'animal', 'house', 'point', 'page', 'letter', 'mother',
            'answer', 'found', 'study', 'still', 'learn', 'should', 'america',
            'world', 'high', 'every', 'near', 'add', 'food', 'between',
            'own', 'below', 'country', 'plant', 'last', 'school', 'father',
            'keep', 'tree', 'never', 'start', 'city', 'earth', 'eye',
            'light', 'thought', 'head', 'under', 'story', 'saw', 'left',
            'don\'t', 'few', 'while', 'along', 'might', 'close', 'something',
            'seem', 'next', 'hard', 'open', 'example', 'begin', 'life',
            'always', 'those', 'both', 'paper', 'together', 'got', 'group',
            'often', 'run', 'important', 'until', 'children', 'side',
            'feet', 'car', 'mile', 'night', 'walk', 'white', 'sea',
            'began', 'grow', 'took', 'river', 'four', 'carry', 'state',
            'once', 'book', 'hear', 'stop', 'without', 'second', 'late',
            'miss', 'idea', 'enough', 'eat', 'face', 'watch', 'far',
            'Indian', 'real', 'almost', 'let', 'above', 'girl', 'sometimes',
            'mountain', 'cut', 'young', 'talk', 'soon', 'list', 'song',
            'being', 'leave', 'family', 'it\'s', 'body', 'music', 'color',
            'stand', 'sun', 'questions', 'fish', 'area', 'mark', 'dog',
            'horse', 'birds', 'problem', 'complete', 'room', 'knew',
            'since', 'ever', 'piece', 'told', 'usually', 'didn\'t',
            'friends', 'easy', 'heard', 'order', 'red', 'door', 'sure',
            'become', 'top', 'ship', 'across', 'today', 'during', 'short',
            'better', 'best', 'however', 'low', 'hours', 'black', 'products',
            'happened', 'whole', 'measure', 'remember', 'early', 'waves',
            'reached', 'listen', 'wind', 'rock', 'space', 'covered',
            'fast', 'several', 'hold', 'himself', 'toward', 'five',
            'step', 'morning', 'passed', 'vowel', 'true', 'hundred',
            'against', 'pattern', 'numeral', 'table', 'north', 'slowly',
            'money', 'map', 'farm', 'pulled', 'draw', 'voice', 'seen',
            'cold', 'cried', 'plan', 'notice', 'south', 'sing', 'war',
            'ground', 'fall', 'king', 'town', 'I\'ll', 'unit', 'figure',
            'certain', 'field', 'travel', 'wood', 'fire', 'upon'
        }
    
    def clean_html(self, text: str) -> str:
        """
        Remove HTML tags and decode HTML entities.
        
        Args:
            text: Text containing HTML
            
        Returns:
            Cleaned text without HTML
        """
        if not text:
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace characters.
        
        Args:
            text: Text with inconsistent whitespace
            
        Returns:
            Text with normalized whitespace
        """
        if not text:
            return ""
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def remove_special_characters(self, text: str, keep_punctuation: bool = True) -> str:
        """
        Remove special characters while optionally keeping punctuation.
        
        Args:
            text: Text with special characters
            keep_punctuation: Whether to keep punctuation marks
            
        Returns:
            Text with special characters removed
        """
        if not text:
            return ""
        
        if keep_punctuation:
            # Keep letters, numbers, spaces, and common punctuation
            text = re.sub(r'[^\w\s.,!?;:()\-/\'"]', '', text)
        else:
            # Keep only letters, numbers, and spaces
            text = re.sub(r'[^\w\s]', '', text)
        
        return text
    
    def normalize_location(self, location: str) -> str:
        """
        Normalize location text for consistency.
        
        Args:
            location: Location string to normalize
            
        Returns:
            Normalized location string
        """
        if not location:
            return ""
        
        # Convert to lowercase for processing
        location_lower = location.lower()
        
        # Replace common abbreviations
        for abbrev, full in self.location_abbreviations.items():
            location_lower = location_lower.replace(abbrev, full)
        
        # Handle common variations
        location_lower = location_lower.replace('st louis', 'saint louis')
        location_lower = location_lower.replace('new york city', 'new york')
        location_lower = location_lower.replace('los angeles', 'la')
        
        # Capitalize properly
        words = location_lower.split(', ')
        if len(words) >= 2:
            city = words[0].title()
            state = words[1].upper()
            return f"{city}, {state}"
        
        return location_lower.title()
    
    def normalize_job_title(self, title: str) -> str:
        """
        Normalize job title for consistency.
        
        Args:
            title: Job title to normalize
            
        Returns:
            Normalized job title
        """
        if not title:
            return ""
        
        # Convert to lowercase for processing
        title_lower = title.lower()
        
        # Replace common abbreviations
        for abbrev, full in self.job_abbreviations.items():
            title_lower = title_lower.replace(abbrev, full)
        
        # Handle common variations
        title_lower = title_lower.replace('software eng', 'software engineer')
        title_lower = title_lower.replace('data sci', 'data scientist')
        title_lower = title_lower.replace('front end', 'frontend')
        title_lower = title_lower.replace('back end', 'backend')
        title_lower = title_lower.replace('full stack', 'fullstack')
        
        # Title case the result
        return title_lower.title()
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from text using keyword matching.
        
        Args:
            text: Text to extract skills from
            
        Returns:
            List of extracted skills
        """
        if not text:
            return []
        
        # Common programming languages and technologies
        skills_keywords = [
            'python', 'java', 'javascript', 'js', 'typescript', 'ts',
            'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin',
            'scala', 'r', 'matlab', 'sql', 'html', 'css', 'xml', 'json',
            'react', 'angular', 'vue', 'node.js', 'express', 'django',
            'flask', 'spring', 'laravel', 'asp.net', 'jquery', 'bootstrap',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
            'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial',
            'linux', 'unix', 'windows', 'macos', 'ubuntu', 'centos',
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            'matplotlib', 'seaborn', 'plotly', 'tableau', 'powerbi',
            'agile', 'scrum', 'kanban', 'waterfall', 'devops', 'ci/cd',
            'rest', 'graphql', 'soap', 'microservices', 'api', 'sdk',
            'machine learning', 'ml', 'artificial intelligence', 'ai',
            'deep learning', 'nlp', 'computer vision', 'data science',
            'statistics', 'analytics', 'etl', 'data warehousing', 'bi',
            'blockchain', 'cryptocurrency', 'bitcoin', 'ethereum',
            'cybersecurity', 'penetration testing', 'ethical hacking',
            'network security', 'information security', 'compliance',
            'gdpr', 'hipaa', 'sox', 'pci', 'iso', 'nist'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skills_keywords:
            if skill in text_lower:
                found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates
    
    def remove_stop_words(self, text: str) -> str:
        """
        Remove common stop words from text.
        
        Args:
            text: Text to remove stop words from
            
        Returns:
            Text with stop words removed
        """
        if not text:
            return ""
        
        words = text.split()
        filtered_words = [word for word in words if word.lower() not in self.stop_words]
        
        return ' '.join(filtered_words)
    
    def lemmatize_text(self, text: str) -> str:
        """
        Basic lemmatization (reduce words to base form).
        This is a simplified version - for production, consider using NLTK or spaCy.
        
        Args:
            text: Text to lemmatize
            
        Returns:
            Lemmatized text
        """
        if not text:
            return ""
        
        # Simple lemmatization rules
        lemmatization_rules = {
            'ing': '',  # running -> run
            'ed': '',   # worked -> work
            'er': '',   # faster -> fast
            'est': '',  # fastest -> fast
            'ly': '',   # quickly -> quick
            'ies': 'y', # studies -> study
            's': '',    # cats -> cat (simplified)
        }
        
        words = text.split()
        lemmatized_words = []
        
        for word in words:
            lemmatized_word = word
            for suffix, replacement in lemmatization_rules.items():
                if word.lower().endswith(suffix):
                    lemmatized_word = word[:-len(suffix)] + replacement
                    break
            lemmatized_words.append(lemmatized_word)
        
        return ' '.join(lemmatized_words)
    
    def clean_job_description(self, description: str) -> str:
        """
        Comprehensive cleaning of job description text.
        
        Args:
            description: Raw job description
            
        Returns:
            Cleaned job description
        """
        if not description:
            return ""
        
        # Remove HTML
        description = self.clean_html(description)
        
        # Remove special characters but keep punctuation
        description = self.remove_special_characters(description, keep_punctuation=True)
        
        # Normalize whitespace
        description = self.normalize_whitespace(description)
        
        # Convert to lowercase for consistency
        description = description.lower()
        
        return description
    
    def clean_resume_text(self, text: str) -> str:
        """
        Clean resume text for processing.
        
        Args:
            text: Raw resume text
            
        Returns:
            Cleaned resume text
        """
        if not text:
            return ""
        
        # Remove HTML
        text = self.clean_html(text)
        
        # Remove special characters but keep punctuation
        text = self.remove_special_characters(text, keep_punctuation=True)
        
        # Normalize whitespace
        text = self.normalize_whitespace(text)
        
        # Convert to lowercase for consistency
        text = text.lower()
        
        return text
    
    def prepare_for_embedding(self, text: str, remove_stop_words: bool = False, 
                            lemmatize: bool = False) -> str:
        """
        Prepare text for embedding by applying various cleaning steps.
        
        Args:
            text: Text to prepare
            remove_stop_words: Whether to remove stop words
            lemmatize: Whether to apply lemmatization
            
        Returns:
            Text prepared for embedding
        """
        if not text:
            return ""
        
        # Basic cleaning
        text = self.clean_html(text)
        text = self.remove_special_characters(text, keep_punctuation=True)
        text = self.normalize_whitespace(text)
        text = text.lower()
        
        # Optional processing
        if remove_stop_words:
            text = self.remove_stop_words(text)
        
        if lemmatize:
            text = self.lemmatize_text(text)
        
        return text 
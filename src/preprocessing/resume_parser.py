"""
Resume parsing and preprocessing utilities.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from .text_cleaner import TextCleaner

logger = logging.getLogger(__name__)

class ResumeParser:
    """Parses and preprocesses resume text to extract key sections."""
    
    def __init__(self):
        self.text_cleaner = TextCleaner()
        
        # Common section headers in resumes
        self.section_headers = {
            'experience': [
                'experience', 'work experience', 'employment history', 
                'professional experience', 'career history', 'work history'
            ],
            'education': [
                'education', 'academic background', 'qualifications', 
                'degrees', 'academic history'
            ],
            'skills': [
                'skills', 'technical skills', 'competencies', 'expertise',
                'technologies', 'programming languages', 'tools'
            ],
            'projects': [
                'projects', 'portfolio', 'personal projects', 'academic projects',
                'work projects', 'achievements'
            ],
            'summary': [
                'summary', 'objective', 'profile', 'about', 'introduction',
                'career objective', 'professional summary'
            ],
            'certifications': [
                'certifications', 'certificates', 'licenses', 'accreditations'
            ],
            'languages': [
                'languages', 'language skills', 'spoken languages'
            ],
            'interests': [
                'interests', 'hobbies', 'activities', 'volunteer work'
            ]
        }
    
    def parse_resume_text(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse resume text and extract key sections.
        
        Args:
            resume_text: Raw resume text
            
        Returns:
            Dictionary containing parsed resume sections
        """
        if not resume_text:
            return {}
        
        # Clean the resume text
        cleaned_text = self.text_cleaner.clean_resume_text(resume_text)
        
        # Split text into sections
        sections = self._extract_sections(cleaned_text)
        
        # Parse each section
        parsed_resume = {
            'raw_text': resume_text,
            'cleaned_text': cleaned_text,
            'parsed_at': datetime.now().isoformat()
        }
        
        # Extract and process each section
        for section_name, section_text in sections.items():
            if section_text:
                parsed_resume[section_name] = self._process_section(section_name, section_text)
        
        # Extract contact information
        contact_info = self._extract_contact_info(resume_text)
        if contact_info:
            parsed_resume['contact_info'] = contact_info
        
        # Extract skills from all sections
        all_skills = self._extract_all_skills(parsed_resume)
        parsed_resume['extracted_skills'] = all_skills
        
        return parsed_resume
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract sections from resume text based on headers.
        
        Args:
            text: Cleaned resume text
            
        Returns:
            Dictionary mapping section names to section text
        """
        sections = {}
        lines = text.split('\n')
        
        current_section = 'summary'  # Default section
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line is a section header
            section_found = False
            for section_name, headers in self.section_headers.items():
                for header in headers:
                    if re.search(rf'\b{re.escape(header)}\b', line.lower()):
                        # Save previous section
                        if current_content:
                            sections[current_section] = '\n'.join(current_content)
                        
                        # Start new section
                        current_section = section_name
                        current_content = []
                        section_found = True
                        break
                if section_found:
                    break
            
            if not section_found:
                current_content.append(line)
        
        # Save the last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _process_section(self, section_name: str, section_text: str) -> Dict[str, Any]:
        """
        Process a specific resume section.
        
        Args:
            section_name: Name of the section
            section_text: Text content of the section
            
        Returns:
            Processed section data
        """
        processed_section = {
            'raw_text': section_text,
            'cleaned_text': self.text_cleaner.normalize_whitespace(section_text),
            'word_count': len(section_text.split()),
            'char_count': len(section_text)
        }
        
        # Section-specific processing
        if section_name == 'experience':
            processed_section.update(self._process_experience_section(section_text))
        elif section_name == 'education':
            processed_section.update(self._process_education_section(section_text))
        elif section_name == 'skills':
            processed_section.update(self._process_skills_section(section_text))
        elif section_name == 'projects':
            processed_section.update(self._process_projects_section(section_text))
        
        return processed_section
    
    def _process_experience_section(self, text: str) -> Dict[str, Any]:
        """Process experience section to extract job details."""
        # Simple extraction - in production, you might use more sophisticated NLP
        lines = text.split('\n')
        experiences = []
        
        current_experience = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for company names (usually in caps or followed by common words)
            if re.search(r'\b[A-Z][A-Z\s&]+(?:Inc|Corp|LLC|Ltd|Company|Technologies|Solutions)\b', line):
                if current_experience:
                    experiences.append(current_experience)
                current_experience = {'company': line}
            elif 'experience' in line.lower() or 'years' in line.lower():
                current_experience['duration'] = line
            else:
                if 'description' not in current_experience:
                    current_experience['description'] = line
                else:
                    current_experience['description'] += ' ' + line
        
        if current_experience:
            experiences.append(current_experience)
        
        return {
            'experiences': experiences,
            'experience_count': len(experiences)
        }
    
    def _process_education_section(self, text: str) -> Dict[str, Any]:
        """Process education section to extract degree information."""
        lines = text.split('\n')
        education_items = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for degree keywords
            degree_keywords = ['bachelor', 'master', 'phd', 'associate', 'diploma', 'certificate']
            if any(keyword in line.lower() for keyword in degree_keywords):
                education_items.append(line)
        
        return {
            'education_items': education_items,
            'education_count': len(education_items)
        }
    
    def _process_skills_section(self, text: str) -> Dict[str, Any]:
        """Process skills section to extract individual skills."""
        # Extract skills using the text cleaner
        skills = self.text_cleaner.extract_skills(text)
        
        # Also look for comma-separated skills
        lines = text.split('\n')
        for line in lines:
            if ',' in line:
                skills.extend([skill.strip() for skill in line.split(',')])
        
        # Remove duplicates and clean
        skills = list(set([skill.strip() for skill in skills if skill.strip()]))
        
        return {
            'skills_list': skills,
            'skills_count': len(skills)
        }
    
    def _process_projects_section(self, text: str) -> Dict[str, Any]:
        """Process projects section to extract project details."""
        lines = text.split('\n')
        projects = []
        
        current_project = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for project names (usually start with capital letters)
            if re.match(r'^[A-Z][A-Za-z\s]+$', line) and len(line) > 3:
                if current_project:
                    projects.append(current_project)
                current_project = {'name': line}
            else:
                if 'description' not in current_project:
                    current_project['description'] = line
                else:
                    current_project['description'] += ' ' + line
        
        if current_project:
            projects.append(current_project)
        
        return {
            'projects': projects,
            'project_count': len(projects)
        }
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from resume."""
        contact_info = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Extract phone number
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()
        
        # Extract LinkedIn URL
        linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9-]+'
        linkedin_match = re.search(linkedin_pattern, text)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group()
        
        # Extract GitHub URL
        github_pattern = r'github\.com/[A-Za-z0-9-]+'
        github_match = re.search(github_pattern, text)
        if github_match:
            contact_info['github'] = github_match.group()
        
        return contact_info
    
    def _extract_all_skills(self, parsed_resume: Dict[str, Any]) -> List[str]:
        """Extract skills from all sections of the resume."""
        all_skills = []
        
        # Extract from skills section
        if 'skills' in parsed_resume:
            skills_section = parsed_resume['skills']
            if 'skills_list' in skills_section:
                all_skills.extend(skills_section['skills_list'])
        
        # Extract from experience section
        if 'experience' in parsed_resume:
            experience_section = parsed_resume['experience']
            if 'raw_text' in experience_section:
                experience_skills = self.text_cleaner.extract_skills(experience_section['raw_text'])
                all_skills.extend(experience_skills)
        
        # Extract from projects section
        if 'projects' in parsed_resume:
            projects_section = parsed_resume['projects']
            if 'raw_text' in projects_section:
                project_skills = self.text_cleaner.extract_skills(projects_section['raw_text'])
                all_skills.extend(project_skills)
        
        # Extract from summary section
        if 'summary' in parsed_resume:
            summary_section = parsed_resume['summary']
            if 'raw_text' in summary_section:
                summary_skills = self.text_cleaner.extract_skills(summary_section['raw_text'])
                all_skills.extend(summary_skills)
        
        # Remove duplicates and return
        return list(set(all_skills))
    
    def create_resume_embedding_text(self, parsed_resume: Dict[str, Any], 
                                   include_sections: List[str] = None) -> str:
        """
        Create text suitable for embedding from parsed resume.
        
        Args:
            parsed_resume: Parsed resume dictionary
            include_sections: List of sections to include (default: all)
            
        Returns:
            Text prepared for embedding
        """
        if include_sections is None:
            include_sections = ['summary', 'experience', 'skills', 'education', 'projects']
        
        embedding_parts = []
        
        for section in include_sections:
            if section in parsed_resume:
                section_data = parsed_resume[section]
                if 'cleaned_text' in section_data:
                    embedding_parts.append(section_data['cleaned_text'])
        
        # Add extracted skills
        if 'extracted_skills' in parsed_resume and parsed_resume['extracted_skills']:
            embedding_parts.append(' '.join(parsed_resume['extracted_skills']))
        
        return ' '.join(embedding_parts)
    
    def prepare_resume_for_embedding(self, resume_text: str, 
                                   remove_stop_words: bool = False,
                                   lemmatize: bool = False) -> str:
        """
        Prepare resume text for embedding with optional preprocessing.
        
        Args:
            resume_text: Raw resume text
            remove_stop_words: Whether to remove stop words
            lemmatize: Whether to apply lemmatization
            
        Returns:
            Text prepared for embedding
        """
        # Parse the resume first
        parsed_resume = self.parse_resume_text(resume_text)
        
        # Create embedding text
        embedding_text = self.create_resume_embedding_text(parsed_resume)
        
        # Apply additional preprocessing
        embedding_text = self.text_cleaner.prepare_for_embedding(
            embedding_text, remove_stop_words, lemmatize
        )
        
        return embedding_text
    
    def generate_resume_summary(self, parsed_resume: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of the parsed resume.
        
        Args:
            parsed_resume: Parsed resume dictionary
            
        Returns:
            Summary statistics
        """
        summary = {
            'total_sections': len([k for k in parsed_resume.keys() if k not in ['raw_text', 'cleaned_text', 'parsed_at', 'contact_info', 'extracted_skills']]),
            'total_skills': len(parsed_resume.get('extracted_skills', [])),
            'has_contact_info': bool(parsed_resume.get('contact_info')),
            'section_stats': {}
        }
        
        # Section-specific statistics
        for section_name, section_data in parsed_resume.items():
            if isinstance(section_data, dict) and 'word_count' in section_data:
                summary['section_stats'][section_name] = {
                    'word_count': section_data['word_count'],
                    'char_count': section_data['char_count']
                }
        
        return summary 
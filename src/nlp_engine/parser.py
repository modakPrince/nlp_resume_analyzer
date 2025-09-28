# resume_parser.py
# A utility module to extract text and structured data from resume files.

import fitz  # PyMuPDF
import spacy
import re
from .config_loader import get_config_loader

# Load the spaCy model for NER
# Make sure you have run: python -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")

# Initialize config loader for dynamic skills loading
config_loader = get_config_loader()

def extract_text_from_pdf(pdf_path):
    """Opens a PDF file and extracts all text from it."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        return f"Error reading PDF file: {e}"

def extract_name(resume_text):
    """Extracts the name from the resume text using spaCy's NER."""
    doc = nlp(resume_text)
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            return ent.text
    return None

def extract_email(resume_text):
    """Extracts the email address from the resume text using regex."""
    match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
    return match.group(0) if match else None

def extract_phone_number(resume_text):
    """Extracts the phone number from the resume text using regex."""
    match = re.search(r'\(?\d{2,3}\)?[-.\s]?\d{5,}[-.\s]?\d{5,}', resume_text)
    return match.group(0) if match else None

def extract_skills(resume_text):
    """Extracts skills from the resume text using YAML configuration with synonym support."""
    found_skills = set()
    resume_text_lower = resume_text.lower()
    
    try:
        # Get skills mapping from config loader
        skills_mapping = config_loader.load_skills()
        
        # Check each skill name and synonym against the resume text
        for skill_variant, canonical_skill in skills_mapping.items():
            if skill_variant in resume_text_lower:
                found_skills.add(canonical_skill)
        
        return list(found_skills)
        
    except Exception as e:
        # Fallback to empty list if config loading fails
        print(f"Warning: Could not load skills configuration: {e}")
        return []


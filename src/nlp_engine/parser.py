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


def extract_action_verbs(resume_text):
    """Extracts and categorizes action verbs from resume text using YAML configuration.
    
    Args:
        resume_text: The full resume text to analyze
        
    Returns:
        Dict with verb counts by tier and total weighted score:
        {
            'impact_verbs': ['led', 'managed'],
            'build_verbs': ['developed', 'created'], 
            'support_verbs': ['assisted', 'helped'],
            'tier_counts': {'impact': 2, 'build': 2, 'support': 2},
            'weighted_score': 14.0,
            'total_verbs': 6
        }
    """
    try:
        # Load action verb configuration
        verb_config = config_loader.load_action_verbs()
        
        # Initialize result structure
        result = {
            'impact_verbs': [],
            'build_verbs': [],
            'support_verbs': [],
            'tier_counts': {'impact': 0, 'build': 0, 'support': 0},
            'weighted_score': 0.0,
            'total_verbs': 0
        }
        
        # Define tier weights
        tier_weights = {
            'impact': 3.0,
            'build': 2.0, 
            'support': 1.0
        }
        
        # Split resume into lines for bullet-level analysis
        lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
        
        # Process each tier
        for tier_key, verbs in verb_config.items():
            tier_name = tier_key.replace('_verbs', '')  # 'impact_verbs' -> 'impact'
            
            if tier_name not in tier_weights:
                continue
                
            found_verbs = []
            
            # Check each line for action verbs (typically at start of bullets)
            for line in lines:
                line_lower = line.lower()
                words = line_lower.split()
                
                if not words:
                    continue
                    
                # Check first few words of each line for action verbs
                for i, word in enumerate(words[:3]):  # Check first 3 words
                    # Clean word (remove punctuation)
                    clean_word = re.sub(r'[^\w]', '', word)
                    
                    if clean_word in verbs:
                        found_verbs.append(clean_word)
                        result['tier_counts'][tier_name] += 1
                        break  # Only count one verb per line
            
            # Store found verbs for this tier
            if tier_key == 'impact_verbs':
                result['impact_verbs'] = list(set(found_verbs))
            elif tier_key == 'build_verbs':
                result['build_verbs'] = list(set(found_verbs))
            elif tier_key == 'support_verbs':
                result['support_verbs'] = list(set(found_verbs))
        
        # Calculate weighted score
        total_score = 0.0
        total_verbs = 0
        
        for tier, count in result['tier_counts'].items():
            weight = tier_weights[tier]
            total_score += count * weight
            total_verbs += count
        
        result['weighted_score'] = total_score
        result['total_verbs'] = total_verbs
        
        return result
        
    except Exception as e:
        print(f"Warning: Could not load action verb configuration: {e}")
        return {
            'impact_verbs': [],
            'build_verbs': [],
            'support_verbs': [],
            'tier_counts': {'impact': 0, 'build': 0, 'support': 0},
            'weighted_score': 0.0,
            'total_verbs': 0
        }


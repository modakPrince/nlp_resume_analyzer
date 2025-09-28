# analyzer.py
# The main script to analyze a resume against a job description.

import re
from sentence_transformers import SentenceTransformer, util
import spacy  # model will be loaded lazily

# Import the extractor functions from our parser module (works both as package & standalone)
try:
    from . import parser  # when imported as part of nlp_engine package
except ImportError:  # fallback when running this file directly: python analyzer.py
    import parser  # type: ignore

"""Lazy model loading

To make importing this module fast (useful for tests and web cold start), we defer
loading heavy NLP models until the first time they're actually needed.
Use warm_up_models() if you want to preload them at app startup.
"""

_similarity_model = None  # type: ignore
_nlp = None  # type: ignore


def _get_similarity_model():
    global _similarity_model
    if _similarity_model is None:
        _similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _similarity_model


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def warm_up_models():
    """Force-load both models (optional)."""
    _ = _get_similarity_model()
    _ = _get_nlp()


# --- Analysis Functions ---
def calculate_similarity(resume_text, job_description):
    """Calculates semantic similarity between resume and job description."""
    model = _get_similarity_model()
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    job_embedding = model.encode(job_description, convert_to_tensor=True)
    cosine_scores = util.cos_sim(resume_embedding, job_embedding)
    return cosine_scores.item()

def get_resume_quality_score(resume_text):
    """
    Calculates a composite quality score based on weighted action verbs, quantifiable
    achievements, and conciseness.
    
    Returns:
        dict: {
            'overall_score': float,
            'action_verb_analysis': dict,
            'quantifiable_score': float, 
            'conciseness_score': float,
            'breakdown': dict
        }
    """
    doc = _get_nlp()(resume_text)
    lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
    
    # Get weighted action verb analysis
    action_verb_analysis = parser.extract_action_verbs(resume_text)
    
    # Calculate action verb score based on weighted tiers
    if lines:
        # Normalize weighted score by number of lines (bullets)
        avg_weight_per_line = action_verb_analysis['weighted_score'] / len(lines)
        
        # Scale to 0-100 (assuming max realistic average weight per line is ~2.0)
        action_verb_score = min(avg_weight_per_line * 50, 100)
    else:
        action_verb_score = 0

    # Quantifiable achievements score
    quantifiable_count = len(re.findall(r'\b\d+\%?\b|\$\d+', resume_text))
    quantifiable_score = min(quantifiable_count * 10, 100)

    # Conciseness score
    sentences = list(doc.sents)
    total_words = sum(len(sent) for sent in sentences)
    avg_words_per_sentence = total_words / len(sentences) if sentences else 0
    conciseness_score = max(0, 100 - (avg_words_per_sentence * 2))

    # Weighted final score (emphasize action verbs more)
    final_score = (action_verb_score * 0.6) + (quantifiable_score * 0.25) + (conciseness_score * 0.15)
    
    return {
        'overall_score': min(final_score, 100),
        'action_verb_analysis': action_verb_analysis,
        'quantifiable_score': quantifiable_score,
        'conciseness_score': conciseness_score,
        'breakdown': {
            'action_verbs': action_verb_score,
            'quantifiable': quantifiable_score,
            'conciseness': conciseness_score
        }
    }

def analyze_keywords(resume_skills, job_description):
    """
    Finds matched and missing skills between the resume and job description.
    Uses the YAML-based skills configuration.
    """
    # Extract potential skills from the job description using a simple regex
    jd_skills = set(re.findall(r'\b[A-Za-z-]+\b', job_description.lower()))
    
    # Get the skills list from YAML configuration
    try:
        from .config_loader import get_config_loader
        config_loader = get_config_loader()
        skills_list = config_loader.get_skills_list()
        
        # Filter against our known skills database for relevance
        required_skills = set(skill for skill in skills_list if skill.lower() in jd_skills)
        
    except Exception as e:
        print(f"Warning: Could not load skills configuration: {e}")
        required_skills = set()
    
    # Convert resume_skills to set for easier operations
    resume_skills_set = set(resume_skills) if resume_skills else set()
    
    matched_skills = required_skills.intersection(resume_skills_set)
    missing_skills = required_skills.difference(resume_skills_set)
    
    return list(matched_skills), list(missing_skills)


# --- Main Execution ---
if __name__ == "__main__":
    sample_resume_path = "data/sample_resumes/sample_resume.pdf"

    job_description = """
    Job Title: Data Science Intern

    We are looking for a motivated Data Science Intern to join our team. The ideal candidate
    will have a strong foundation in machine learning, statistics, and programming. You will
    work on real-world projects, helping us to extract insights from our data.

    Responsibilities:
    - Assist in developing and testing machine learning models.
    - Clean, preprocess, and analyze large datasets.
    - Create data visualizations to communicate findings.
    - Collaborate with the engineering team to deploy models.

    Required Skills:
    - Currently pursuing a degree in Computer Science, Statistics, or a related field.
    - Solid understanding of Python and its data science libraries (Pandas, NumPy, Scikit-learn).
    - Familiarity with SQL for data extraction.
    - Basic knowledge of machine learning concepts.
    - Strong problem-solving skills.
    """
    
    print(f"Attempting to analyze resume from: {sample_resume_path}\n")
    
    resume_text = parser.extract_text_from_pdf(sample_resume_path)
    
    if "Error" not in resume_text:
        # --- Basic Information Extraction ---
        name = parser.extract_name(resume_text)
        email = parser.extract_email(resume_text)
        phone = parser.extract_phone_number(resume_text)
        skills = parser.extract_skills(resume_text)
        
        # --- Advanced Analysis ---
        similarity_score = calculate_similarity(resume_text, job_description)
        quality_score = get_resume_quality_score(resume_text)
        matched_keywords, missing_keywords = analyze_keywords(skills, job_description)
        
        # --- Print Report ---
        print("--- Basic Information ---")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Phone: {phone}\n")
        
        print("--- Advanced Analysis ---")
        print(f"Job Description Match Score: {similarity_score:.2%}")
        print(f"Resume Quality Score: {quality_score:.2f}/100\n")
        
        print("--- Keyword Analysis & Suggestions ---")
        print(f"Skills Found in Resume and Job Description: {matched_keywords}")
        if missing_keywords:
            print(f"SUGGESTION: Consider adding these skills to your resume: {missing_keywords}")
        else:
            print("Excellent! All required skills from the job description were found in the resume.")
        print("--------------------------------------\n")
    else:
        print(f"Could not analyze resume. Error: {resume_text}")

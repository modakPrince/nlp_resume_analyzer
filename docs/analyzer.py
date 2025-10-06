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
    Legacy function - calculates a composite quality score based on weighted action verbs, 
    quantifiable achievements, and conciseness. Now uses the enhanced scoring system internally
    but returns the old format for backward compatibility.
    
    Returns:
        dict: {
            'overall_score': float,
            'action_verb_analysis': dict,
            'quantifiable_score': float, 
            'conciseness_score': float,
            'breakdown': dict
        }
    """
    # Get the enhanced structured scoring
    enhanced_scores = get_enhanced_resume_score(resume_text, job_description=None, legacy_format=False)
    
    # Extract action verb analysis from impact metrics
    action_verb_analysis = enhanced_scores['impact']['details']['action_verb_analysis']
    
    # Map new scores to legacy format
    quantifiable_score = enhanced_scores['impact']['components']['quantified_achievements'] * 100
    conciseness_score = enhanced_scores['clarity']['components']['conciseness'] * 100
    
    # Calculate action verb score in legacy format
    lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
    if lines:
        avg_weight_per_line = action_verb_analysis['weighted_score'] / len(lines)
        action_verb_score = min(avg_weight_per_line * 50, 100)
    else:
        action_verb_score = 0
    
    # Calculate legacy overall score using original weights
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

def get_enhanced_resume_score(resume_text, job_description=None, legacy_format=False):
    """
    Enhanced scoring with structured multi-metrics for relevance, impact, structure, clarity, and gaps.
    
    Args:
        resume_text: The resume content
        job_description: Optional job description for relevance analysis
        legacy_format: If True, returns old flat score format for backward compatibility
    
    Returns:
        dict: Either legacy format or new structured format with detailed metrics
    """
    if legacy_format:
        # Return existing format for backward compatibility
        return get_resume_quality_score(resume_text)
    
    # Calculate structured metrics
    structured_scores = _calculate_structured_metrics(resume_text, job_description)
    return structured_scores


def _calculate_structured_metrics(resume_text, job_description=None):
    """Calculate the five core metrics: relevance, impact, structure, clarity, gaps."""
    doc = _get_nlp()(resume_text)
    lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
    
    # Get existing analysis components
    action_verb_analysis = parser.extract_action_verbs(resume_text)
    
    # 1. RELEVANCE SCORE
    relevance_score = _calculate_relevance_score(resume_text, job_description, doc)
    
    # 2. IMPACT SCORE  
    impact_score = _calculate_impact_score(resume_text, action_verb_analysis, lines, doc)
    
    # 3. STRUCTURE SCORE
    structure_score = _calculate_structure_score(resume_text, lines, doc)
    
    # 4. CLARITY SCORE
    clarity_score = _calculate_clarity_score(resume_text, lines, doc)
    
    # 5. GAPS SCORE
    gaps_score = _calculate_gaps_score(resume_text, job_description)
    
    return {
        "relevance": relevance_score,
        "impact": impact_score, 
        "structure": structure_score,
        "clarity": clarity_score,
        "gaps": gaps_score,
        "overall_score": _calculate_overall_score([relevance_score, impact_score, structure_score, clarity_score, gaps_score]),
        "metadata": {
            "analysis_version": "2.0",
            "legacy_compatible": True,
            "metrics_count": 5
        }
    }


def _calculate_relevance_score(resume_text, job_description, doc):
    """Calculate relevance metrics including semantic similarity and keyword alignment."""
    if not job_description:
        return {
            "score": None,
            "components": {
                "semantic_similarity": None,
                "keyword_match_rate": None,
                "domain_alignment": None
            },
            "explanation": "No job description provided for relevance analysis"
        }
    
    # Semantic similarity (existing logic)
    semantic_similarity = calculate_similarity(resume_text, job_description)
    
    # Keyword match rate
    resume_skills = parser.extract_skills(resume_text)
    matched_keywords, missing_keywords = analyze_keywords(resume_skills, job_description)
    
    total_jd_skills = len(matched_keywords) + len(missing_keywords)
    keyword_match_rate = len(matched_keywords) / max(total_jd_skills, 1)
    
    # Domain alignment (simplified heuristic based on technical terms)
    technical_terms = len(re.findall(r'\b(?:API|SDK|CI/CD|DevOps|ML|AI|database|framework|algorithm)\b', resume_text, re.IGNORECASE))
    jd_technical_terms = len(re.findall(r'\b(?:API|SDK|CI/CD|DevOps|ML|AI|database|framework|algorithm)\b', job_description, re.IGNORECASE))
    domain_alignment = min(technical_terms / max(jd_technical_terms, 1), 1.0) if jd_technical_terms > 0 else 0.5
    
    # Composite relevance score (0-100)
    relevance_score = (semantic_similarity * 40) + (keyword_match_rate * 40) + (domain_alignment * 20)
    
    return {
        "score": min(relevance_score * 100, 100),
        "components": {
            "semantic_similarity": semantic_similarity,
            "keyword_match_rate": keyword_match_rate,
            "domain_alignment": domain_alignment
        },
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords
    }


def _calculate_impact_score(resume_text, action_verb_analysis, lines, doc):
    """Calculate impact metrics including quantified achievements and leadership indicators."""
    # Quantified achievements
    quantifiable_patterns = re.findall(r'\b\d+(?:\.\d+)?(?:%|K|M|B)?\b|\$\d+(?:,\d{3})*(?:\.\d{2})?[KMB]?', resume_text)
    quantifiable_score = min(len(quantifiable_patterns) * 8, 100)
    
    # Leadership indicators
    leadership_patterns = re.findall(r'\b(?:led|managed|supervised|directed|mentored|coached|guided|spearheaded)\b', resume_text, re.IGNORECASE)
    leadership_score = min(len(leadership_patterns) * 15, 100)
    
    # Action verb strength (from existing analysis)
    action_verb_strength = min(action_verb_analysis['weighted_score'] / max(len(lines), 1) * 50, 100)
    
    # Measurable outcomes (results-oriented language)
    outcome_patterns = re.findall(r'\b(?:increased|decreased|improved|reduced|achieved|delivered|generated|saved|optimized)\b', resume_text, re.IGNORECASE)
    outcome_score = min(len(outcome_patterns) * 10, 100)
    
    # Composite impact score
    impact_score = (action_verb_strength * 0.4) + (quantifiable_score * 0.3) + (leadership_score * 0.2) + (outcome_score * 0.1)
    
    return {
        "score": min(impact_score, 100),
        "components": {
            "quantified_achievements": quantifiable_score / 100,
            "leadership_indicators": leadership_score / 100,
            "action_verb_strength": action_verb_strength / 100,
            "measurable_outcomes": outcome_score / 100
        },
        "details": {
            "quantifiable_count": len(quantifiable_patterns),
            "leadership_count": len(leadership_patterns),
            "outcome_count": len(outcome_patterns),
            "action_verb_analysis": action_verb_analysis
        }
    }


def _calculate_structure_score(resume_text, lines, doc):
    """Calculate structure metrics including organization and formatting consistency."""
    # Section detection (simplified)
    sections = re.findall(r'^(?:EXPERIENCE|EDUCATION|SKILLS|PROJECTS|SUMMARY|OBJECTIVE|CONTACT)', resume_text, re.MULTILINE | re.IGNORECASE)
    section_organization = min(len(sections) * 20, 100)
    
    # Contact information completeness
    has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text))
    has_phone = bool(re.search(r'\(?\d{2,3}\)?[-.\s]?\d{5,}[-.\s]?\d{5,}', resume_text))
    contact_completeness = (int(has_email) + int(has_phone)) * 50
    
    # Length appropriateness (1-2 pages ideal)
    word_count = len(resume_text.split())
    if 300 <= word_count <= 800:
        length_score = 100
    elif 200 <= word_count < 300 or 800 < word_count <= 1200:
        length_score = 70
    else:
        length_score = 40
    
    # Information hierarchy (bullet points and formatting)
    bullet_indicators = len(re.findall(r'^[\s]*[•\-\*]\s', resume_text, re.MULTILINE))
    hierarchy_score = min(bullet_indicators * 5, 100) if bullet_indicators > 0 else 30
    
    # Composite structure score
    structure_score = (section_organization * 0.3) + (contact_completeness * 0.2) + (length_score * 0.25) + (hierarchy_score * 0.25)
    
    return {
        "score": min(structure_score, 100),
        "components": {
            "section_organization": section_organization / 100,
            "contact_completeness": contact_completeness / 100,  
            "length_appropriateness": length_score / 100,
            "information_hierarchy": hierarchy_score / 100
        },
        "details": {
            "sections_found": len(sections),
            "has_email": has_email,
            "has_phone": has_phone,
            "word_count": word_count,
            "bullet_points": bullet_indicators
        }
    }


def _calculate_clarity_score(resume_text, lines, doc):
    """Calculate clarity metrics including conciseness and readability."""
    sentences = list(doc.sents)
    
    # Conciseness (existing logic enhanced)
    total_words = sum(len(sent.text.split()) for sent in sentences)
    avg_words_per_sentence = total_words / len(sentences) if sentences else 0
    
    if avg_words_per_sentence <= 15:
        conciseness_score = 100
    elif avg_words_per_sentence <= 20:
        conciseness_score = 80
    elif avg_words_per_sentence <= 25:
        conciseness_score = 60
    else:
        conciseness_score = max(0, 100 - (avg_words_per_sentence - 25) * 4)
    
    # Readability (simplified Flesch-like heuristic)
    avg_sentence_length = len(sentences) / max(len(resume_text.split('.')), 1)
    complex_words = len([token for token in doc if len(token.text) > 6 and token.is_alpha])
    total_words_count = len([token for token in doc if token.is_alpha])
    complex_word_ratio = complex_words / max(total_words_count, 1)
    
    readability_score = max(0, 100 - (complex_word_ratio * 100) - (max(0, avg_sentence_length - 1.5) * 20))
    
    # Technical precision (appropriate use of industry terms)
    technical_terms = len(re.findall(r'\b(?:[A-Z]{2,}|[A-Z][a-z]+(?:[A-Z][a-z]+)+)\b', resume_text))
    precision_score = min(technical_terms * 3, 100)
    
    # Composite clarity score
    clarity_score = (conciseness_score * 0.5) + (readability_score * 0.3) + (precision_score * 0.2)
    
    return {
        "score": min(clarity_score, 100),
        "components": {
            "conciseness": conciseness_score / 100,
            "readability": readability_score / 100,
            "technical_precision": precision_score / 100
        },
        "details": {
            "avg_words_per_sentence": avg_words_per_sentence,
            "complex_word_ratio": complex_word_ratio,
            "technical_terms_count": technical_terms
        }
    }


def _calculate_gaps_score(resume_text, job_description):
    """Calculate gaps analysis - lower score means fewer gaps (inverse scoring)."""
    if not job_description:
        return {
            "score": 100,  # No gaps can be identified without job description
            "identified_gaps": [],
            "critical_missing": [],
            "improvement_suggestions": [],
            "explanation": "No job description provided for gap analysis"
        }
    
    # Get skill analysis
    resume_skills = parser.extract_skills(resume_text)
    matched_keywords, missing_keywords = analyze_keywords(resume_skills, job_description)
    
    # Calculate gap severity
    total_expected_skills = len(matched_keywords) + len(missing_keywords)
    missing_ratio = len(missing_keywords) / max(total_expected_skills, 1)
    
    # Identify critical vs nice-to-have missing skills (simplified heuristic)
    critical_missing = []
    improvement_suggestions = []
    
    for skill in missing_keywords[:5]:  # Top 5 missing
        if any(term in job_description.lower() for term in [skill.lower(), 'required', 'must have']):
            critical_missing.append(skill)
            improvement_suggestions.append(f"Add experience with {skill} - appears to be a key requirement")
        else:
            improvement_suggestions.append(f"Consider adding {skill} to strengthen your profile")
    
    # Gaps score (inverse - lower is better, but we display as "completion score")
    completion_score = max(0, 100 - (missing_ratio * 100))
    
    return {
        "score": completion_score,
        "identified_gaps": missing_keywords,
        "critical_missing": critical_missing,
        "improvement_suggestions": improvement_suggestions[:3],  # Top 3 suggestions
        "gap_analysis": {
            "total_skills_identified": total_expected_skills,
            "skills_present": len(matched_keywords), 
            "skills_missing": len(missing_keywords),
            "completion_rate": (len(matched_keywords) / max(total_expected_skills, 1)) * 100
        }
    }


def _calculate_overall_score(metric_scores):
    """Calculate weighted overall score from individual metrics."""
    # Extract numeric scores, handling None values
    scores = []
    weights = []
    
    # Relevance (25% weight)
    if metric_scores[0]["score"] is not None:
        scores.append(metric_scores[0]["score"])
        weights.append(0.25)
    
    # Impact (30% weight)
    scores.append(metric_scores[1]["score"])
    weights.append(0.30)
    
    # Structure (20% weight) 
    scores.append(metric_scores[2]["score"])
    weights.append(0.20)
    
    # Clarity (15% weight)
    scores.append(metric_scores[3]["score"])
    weights.append(0.15)
    
    # Gaps (10% weight)
    scores.append(metric_scores[4]["score"])
    weights.append(0.10)
    
    # Normalize weights if relevance is missing
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]
    
    # Calculate weighted average
    overall_score = sum(score * weight for score, weight in zip(scores, normalized_weights))
    return min(overall_score, 100)


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

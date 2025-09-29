# app.py
# The Flask web server for our Resume Analyzer application.

from flask import Flask, render_template, request, redirect, url_for
import os
import sys
import uuid  # To generate unique filenames

# --- Ensure the parent 'src' directory (which contains the 'nlp_engine' package) is on sys.path ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # points to .../src
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import parser module & analysis functions
from nlp_engine import (
    parser as resume_parser,
    calculate_similarity,
    get_resume_quality_score,
    get_enhanced_resume_score,
    analyze_keywords,
)

# Initialize the Flask application
app = Flask(__name__)

# Configure a folder to temporarily store uploaded resumes
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    """Renders the main page (index.html)."""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze_resume():
    """Handles the form submission and displays the analysis results."""
    if 'resume' not in request.files:
        return "No resume file found!", 400

    resume_file = request.files['resume']
    job_description = request.form.get('job_description', '')

    if resume_file.filename == '':
        return "No selected file!", 400

    if resume_file:  # Allow empty job description for quality-only mode
        # Create a unique filename to prevent overwrites
        unique_filename = str(uuid.uuid4()) + os.path.splitext(resume_file.filename)[1]
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        resume_file.save(resume_path)

        # --- Run the analysis using our backend scripts ---
        resume_text = resume_parser.extract_text_from_pdf(resume_path)

        if "Error" in resume_text:
            os.remove(resume_path)  # Clean up the saved file
            return f"Could not process the uploaded file. Error: {resume_text}", 500

        # Extract basic info
        name = resume_parser.extract_name(resume_text)
        email = resume_parser.extract_email(resume_text)
        phone = resume_parser.extract_phone_number(resume_text)
        skills = resume_parser.extract_skills(resume_text)

        # Perform advanced analysis using enhanced scoring system
        # Handle empty job description (quality-check mode)
        jd_for_analysis = job_description.strip() if job_description else None
        enhanced_analysis = get_enhanced_resume_score(resume_text, jd_for_analysis, legacy_format=False)
        
        # Maintain backward compatibility for existing template
        if enhanced_analysis['relevance']['score'] is not None:
            similarity_score = enhanced_analysis['relevance']['components']['semantic_similarity']
            matched_keywords = enhanced_analysis['relevance']['matched_keywords']
            missing_keywords = enhanced_analysis['relevance']['missing_keywords']
        else:
            similarity_score = 0
            matched_keywords, missing_keywords = ([], [])
        
        legacy_quality_analysis = get_resume_quality_score(resume_text)  # For backward compatibility

        # Clean up the uploaded file after processing
        os.remove(resume_path)

        # Package results with both legacy and enhanced data
        results = {
            # Legacy format for backward compatibility
            'name': name,
            'email': email,
            'phone': phone,
            'similarity_score': f"{similarity_score:.2%}",
            'quality_score': f"{legacy_quality_analysis['overall_score']:.2f}",
            'matched_keywords': matched_keywords,
            'missing_keywords': missing_keywords,
            'quality_analysis': legacy_quality_analysis,
            'action_verb_analysis': legacy_quality_analysis['action_verb_analysis'],
            
            # Enhanced structured analysis
            'enhanced_analysis': enhanced_analysis,
            'has_enhanced_data': True
        }

        # Render the results page with the analysis data
        return render_template('results.html', results=results)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

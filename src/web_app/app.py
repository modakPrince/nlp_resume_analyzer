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

    if resume_file and job_description:
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

        # Perform advanced analysis
        similarity_score = calculate_similarity(resume_text, job_description)
        quality_analysis = get_resume_quality_score(resume_text)
        matched_keywords, missing_keywords = analyze_keywords(skills, job_description)

        # Clean up the uploaded file after processing
        os.remove(resume_path)

        # Package results into a dictionary with enhanced action verb analysis
        results = {
            'name': name,
            'email': email,
            'phone': phone,
            'similarity_score': f"{similarity_score:.2%}",
            'quality_score': f"{quality_analysis['overall_score']:.2f}",
            'matched_keywords': matched_keywords,
            'missing_keywords': missing_keywords,
            'quality_analysis': quality_analysis,  # Include full analysis for UI
            'action_verb_analysis': quality_analysis['action_verb_analysis']
        }

        # Render the results page with the analysis data
        return render_template('results.html', results=results)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

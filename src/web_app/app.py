# app.py
# The Flask web server for our Resume Analyzer application.

from flask import Flask, render_template, request, redirect, url_for
import os
import sys
import uuid  # To generate unique filenames
import json  # For storing results in database
import csv  # For CSV export
from io import StringIO
from flask import Response  # For file downloads

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
from nlp_engine.config_loader import get_config_loader
import yaml

# Initialize the Flask application
app = Flask(__name__)

# Configure database
# Database file will be stored in: project_root/data/resume_analyzer.db
DATABASE_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'data', 'resume_analyzer.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable Flask-SQLAlchemy event system
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'  # For session management

# Import and initialize database
from models import db, Analysis
db.init_app(app)

# Create all database tables
with app.app_context():
    db.create_all()
    print(f"✅ Database initialized at: {DATABASE_PATH}")

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
        is_quality_mode = not jd_for_analysis  # Detect Quality Check Mode
        
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
            # Mode detection
            'mode': 'quality_check' if is_quality_mode else 'full_analysis',
            'is_quality_mode': is_quality_mode,
            
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
        
        # --- Save analysis to database ---
        try:
            # Create preview from first 500 characters
            resume_preview = resume_text[:500] if resume_text else ""
            
            # Calculate job match score (0 if quality mode)
            job_match = enhanced_analysis['relevance']['score'] if not is_quality_mode and enhanced_analysis['relevance']['score'] is not None else 0.0
            
            # Calculate quality score from clarity, structure, and impact (average of non-relevance scores)
            quality_components = [
                enhanced_analysis['clarity']['score'],
                enhanced_analysis['structure']['score'],
                enhanced_analysis['impact']['score']
            ]
            quality_score = sum(quality_components) / len(quality_components)
            
            # Create database record
            analysis_record = Analysis(
                filename=resume_file.filename,
                extracted_name=name,
                extracted_email=email,
                extracted_phone=phone,
                mode='quality_check' if is_quality_mode else 'full_analysis',
                quality_score=quality_score,
                job_match_score=job_match,
                impact_score=enhanced_analysis['impact']['score'],
                structure_score=enhanced_analysis['structure']['score'],
                overall_score=enhanced_analysis['overall_score'],
                results_json=json.dumps(results),  # Store complete results
                resume_preview=resume_preview,
                skills_count=len(skills),
                matched_keywords_count=len(matched_keywords),
                missing_keywords_count=len(missing_keywords)
            )
            
            db.session.add(analysis_record)
            db.session.commit()
            
            # Add the database ID to results for potential use
            results['analysis_id'] = analysis_record.id
            
        except Exception as e:
            print(f"⚠️ Warning: Failed to save analysis to database: {str(e)}")
            # Continue anyway - don't fail the request if database save fails

        # Render the results page with the analysis data
        return render_template('results.html', results=results)

    return redirect(url_for('index'))


@app.route('/skills')
def skills_explorer():
    """Renders the skills database explorer page."""
    # Load the raw skills data from YAML to preserve category structure
    config_path = os.path.abspath(os.path.join(BASE_DIR, '..', 'config'))
    skills_file = os.path.join(config_path, 'skills.yaml')
    
    try:
        with open(skills_file, 'r', encoding='utf-8') as f:
            skills_data = yaml.safe_load(f)
        
        # Transform category names to be more readable
        category_display_names = {
            'programming_languages': 'Programming Languages',
            'web_frameworks': 'Web Frameworks',
            'data_science_libraries': 'Data Science Libraries',
            'cloud_platforms': 'Cloud Platforms',
            'devops_tools': 'DevOps Tools',
            'databases': 'Databases',
            'project_management': 'Project Management',
            'testing_frameworks': 'Testing Frameworks',
            'mobile_development': 'Mobile Development',
            'machine_learning': 'Machine Learning',
            'operating_systems': 'Operating Systems',
            'soft_skills': 'Soft Skills',
            'methodologies': 'Methodologies',
            'other_tools': 'Other Tools'
        }
        
        # Organize data by category with display names
        organized_skills = {}
        total_skills = 0
        total_synonyms = 0
        
        for category_key, skills_list in skills_data.items():
            display_name = category_display_names.get(category_key, category_key.replace('_', ' ').title())
            organized_skills[display_name] = skills_list
            total_skills += len(skills_list)
            for skill in skills_list:
                if 'synonyms' in skill:
                    total_synonyms += len(skill['synonyms'])
        
        stats = {
            'total_categories': len(organized_skills),
            'total_skills': total_skills,
            'total_synonyms': total_synonyms
        }
        
        return render_template('skills.html', skills_data=organized_skills, stats=stats)
    except Exception as e:
        return f"Error loading skills data: {str(e)}", 500


@app.route('/history')
def history():
    """Displays the analysis history page with all saved analyses."""
    # Get filter parameters from query string
    mode_filter = request.args.get('mode', 'all')
    search_query = request.args.get('search', '').strip()
    
    # Build query
    query = Analysis.query
    
    # Apply mode filter
    if mode_filter != 'all':
        query = query.filter_by(mode=mode_filter)
    
    # Apply search filter (search in filename and extracted name)
    if search_query:
        query = query.filter(
            db.or_(
                Analysis.filename.ilike(f'%{search_query}%'),
                Analysis.extracted_name.ilike(f'%{search_query}%')
            )
        )
    
    # Order by most recent first
    analyses = query.order_by(Analysis.upload_date.desc()).all()
    
    # Get statistics
    stats = Analysis.get_statistics()
    
    return render_template('history.html', 
                         analyses=analyses, 
                         stats=stats,
                         current_filter=mode_filter,
                         search_query=search_query)


@app.route('/analysis/<int:analysis_id>')
def view_analysis(analysis_id):
    """Displays a single saved analysis from the database."""
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Get the full results from JSON
    results = analysis.get_results()
    
    # Add database metadata
    results['db_metadata'] = {
        'id': analysis.id,
        'upload_date': analysis.upload_date.strftime('%B %d, %Y at %I:%M %p'),
        'filename': analysis.filename
    }
    
    return render_template('results.html', results=results, from_history=True)


@app.route('/analysis/<int:analysis_id>/delete', methods=['POST'])
def delete_analysis(analysis_id):
    """Deletes a saved analysis from the database."""
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        db.session.delete(analysis)
        db.session.commit()
        return redirect(url_for('history'))
    except Exception as e:
        return f"Error deleting analysis: {str(e)}", 500


@app.route('/export/csv')
def export_csv():
    """Exports filtered analyses to CSV file."""
    # Get filter parameters (same as history page)
    mode_filter = request.args.get('mode', 'all')
    search_query = request.args.get('search', '').strip()
    
    # Build query
    query = Analysis.query
    
    # Apply mode filter
    if mode_filter != 'all':
        query = query.filter_by(mode=mode_filter)
    
    # Apply search filter
    if search_query:
        query = query.filter(
            db.or_(
                Analysis.filename.ilike(f'%{search_query}%'),
                Analysis.extracted_name.ilike(f'%{search_query}%')
            )
        )
    
    # Order by most recent first
    analyses = query.order_by(Analysis.upload_date.desc()).all()
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID',
        'Upload Date',
        'Filename',
        'Name',
        'Email',
        'Phone',
        'Mode',
        'Quality Score',
        'Job Match Score',
        'Impact Score',
        'Structure Score',
        'Overall Score',
        'Skills Count',
        'Matched Keywords',
        'Missing Keywords'
    ])
    
    # Write data rows
    for analysis in analyses:
        writer.writerow([
            analysis.id,
            analysis.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
            analysis.filename,
            analysis.extracted_name or '',
            analysis.extracted_email or '',
            analysis.extracted_phone or '',
            analysis.mode,
            f"{analysis.quality_score:.2f}",
            f"{analysis.job_match_score:.2f}" if analysis.mode == 'full_analysis' else 'N/A',
            f"{analysis.impact_score:.2f}",
            f"{analysis.structure_score:.2f}",
            f"{analysis.overall_score:.2f}",
            analysis.skills_count or 0,
            analysis.matched_keywords_count or 0,
            analysis.missing_keywords_count or 0
        ])
    
    # Create response with CSV file
    output.seek(0)
    
    # Generate filename with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"resume_analyses_{timestamp}.csv"
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


@app.route('/analysis/<int:analysis_id>/export/json')
def export_single_json(analysis_id):
    """Exports a single analysis as JSON file."""
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Get the dictionary representation
    analysis_dict = analysis.to_dict()
    
    # Generate filename
    from datetime import datetime
    safe_filename = analysis.filename.replace('.pdf', '').replace('.docx', '').replace(' ', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"analysis_{safe_filename}_{timestamp}.json"
    
    # Create JSON response
    return Response(
        json.dumps(analysis_dict, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

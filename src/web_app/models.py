# models.py
# Database models for Resume Analyzer application

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# Initialize SQLAlchemy
db = SQLAlchemy()


class Analysis(db.Model):
    """
    Model to store resume analysis results.
    Each record represents one resume analysis (either quality check or full analysis).
    """
    __tablename__ = 'analyses'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # File Information
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Extracted Resume Information (for quick display)
    extracted_name = db.Column(db.String(100), nullable=True)
    extracted_email = db.Column(db.String(100), nullable=True)
    extracted_phone = db.Column(db.String(50), nullable=True)
    
    # Analysis Mode
    mode = db.Column(db.String(20), nullable=False)  # 'quality_check' or 'full_analysis'
    
    # Scores (indexed for filtering/sorting)
    quality_score = db.Column(db.Float, nullable=False)
    job_match_score = db.Column(db.Float, nullable=True)  # None in quality check mode
    impact_score = db.Column(db.Float, nullable=True)
    structure_score = db.Column(db.Float, nullable=True)
    overall_score = db.Column(db.Float, nullable=True)
    
    # Complete Results (JSON)
    results_json = db.Column(db.Text, nullable=False)
    
    # Resume Preview (first 500 characters for display)
    resume_preview = db.Column(db.String(500), nullable=True)
    
    # Metadata
    skills_count = db.Column(db.Integer, default=0)
    matched_keywords_count = db.Column(db.Integer, default=0)
    missing_keywords_count = db.Column(db.Integer, default=0)
    
    # Indexes for faster queries
    __table_args__ = (
        db.Index('idx_upload_date', 'upload_date'),
        db.Index('idx_mode', 'mode'),
        db.Index('idx_quality_score', 'quality_score'),
        db.Index('idx_job_match_score', 'job_match_score'),
    )
    
    def __repr__(self):
        return f'<Analysis {self.id}: {self.filename} ({self.mode})>'
    
    def get_results(self):
        """
        Parse and return the stored JSON results.
        
        Returns:
            dict: The complete analysis results
        """
        try:
            return json.loads(self.results_json)
        except json.JSONDecodeError:
            return {}
    
    def to_dict(self):
        """
        Convert analysis to dictionary for API responses or exports.
        
        Returns:
            dict: Analysis data as dictionary
        """
        return {
            'id': self.id,
            'filename': self.filename,
            'upload_date': self.upload_date.isoformat(),
            'mode': self.mode,
            'quality_score': self.quality_score,
            'job_match_score': self.job_match_score,
            'impact_score': self.impact_score,
            'structure_score': self.structure_score,
            'overall_score': self.overall_score,
            'extracted_name': self.extracted_name,
            'extracted_email': self.extracted_email,
            'extracted_phone': self.extracted_phone,
            'skills_count': self.skills_count,
            'matched_keywords_count': self.matched_keywords_count,
            'missing_keywords_count': self.missing_keywords_count,
            'resume_preview': self.resume_preview,
        }
    
    @staticmethod
    def get_statistics():
        """
        Get summary statistics of all analyses.
        
        Returns:
            dict: Statistics including total analyses, average scores, etc.
        """
        total = Analysis.query.count()
        quality_mode = Analysis.query.filter_by(mode='quality_check').count()
        full_mode = Analysis.query.filter_by(mode='full_analysis').count()
        
        avg_quality = db.session.query(db.func.avg(Analysis.quality_score)).scalar() or 0
        avg_job_match = db.session.query(db.func.avg(Analysis.job_match_score)).filter(
            Analysis.job_match_score.isnot(None)
        ).scalar() or 0
        
        return {
            'total_analyses': total,
            'quality_check_count': quality_mode,
            'full_analysis_count': full_mode,
            'average_quality_score': round(avg_quality, 2),
            'average_job_match_score': round(avg_job_match, 2),
        }

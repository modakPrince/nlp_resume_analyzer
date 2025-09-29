"""
Test cases for the Resume Analyzer
"""

import unittest
import os
import tempfile
from src.nlp_engine.analyzer import (
    get_resume_quality_score, 
    get_enhanced_resume_score, 
    calculate_similarity,
    analyze_keywords
)
from src.nlp_engine import parser


class TestResumeAnalyzer(unittest.TestCase):
    """Test cases for the main analyzer functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        
        # Sample job description
        self.job_description = """
        Software Engineer Position
        
        We are looking for a skilled Software Engineer to join our team.
        
        Responsibilities:
        - Develop web applications using Python and JavaScript
        - Work with SQL databases
        - Collaborate using Git and Agile methodologies
        - Deploy applications to AWS cloud
        
        Requirements:
        - Bachelor's degree in Computer Science
        - 3+ years of Python development experience
        - Experience with React and Node.js
        - Knowledge of Docker and Kubernetes
        - Strong problem-solving skills
        """
        
        # Sample resume text
        self.sample_resume_text = """
        John Doe
        john.doe@email.com
        (555) 123-4567
        
        EXPERIENCE
        Senior Software Developer - Tech Corp (2020-2023)
        - Led a team of 5 developers in building scalable web applications using Python and React
        - Implemented microservices architecture with Docker containers
        - Managed CI/CD pipelines and AWS deployments
        - Improved system performance by 40% through database optimization
        
        Software Engineer - StartupCo (2018-2020)
        - Developed RESTful APIs using Python Flask
        - Built responsive frontend applications with JavaScript and React
        - Worked with PostgreSQL databases and implemented automated testing
        - Collaborated with cross-functional teams using Agile methodologies
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology (2014-2018)
        
        SKILLS
        Python, JavaScript, React, Node.js, SQL, PostgreSQL, AWS, Docker, Git, Agile
        """
    
    def create_temp_text_file(self, content):
        """Create a temporary text file with given content."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def test_legacy_quality_score(self):
        """Test backward compatibility of legacy quality scoring."""
        quality_analysis = get_resume_quality_score(self.sample_resume_text)
        
        # Check expected structure
        self.assertIn('overall_score', quality_analysis)
        self.assertIn('action_verb_analysis', quality_analysis)
        self.assertIn('quantifiable_score', quality_analysis)
        self.assertIn('conciseness_score', quality_analysis)
        self.assertIn('breakdown', quality_analysis)
        
        # Check score ranges
        self.assertGreaterEqual(quality_analysis['overall_score'], 0)
        self.assertLessEqual(quality_analysis['overall_score'], 100)
    
    def test_enhanced_scoring_system(self):
        """Test new enhanced multi-metric scoring system."""
        enhanced_analysis = get_enhanced_resume_score(self.sample_resume_text, self.job_description)
        
        # Check main structure
        self.assertIn('relevance', enhanced_analysis)
        self.assertIn('impact', enhanced_analysis)
        self.assertIn('structure', enhanced_analysis)
        self.assertIn('clarity', enhanced_analysis)
        self.assertIn('gaps', enhanced_analysis)
        self.assertIn('overall_score', enhanced_analysis)
        self.assertIn('metadata', enhanced_analysis)
        
        # Check each metric has required structure
        for metric in ['relevance', 'impact', 'structure', 'clarity']:
            if enhanced_analysis[metric]['score'] is not None:
                self.assertIn('score', enhanced_analysis[metric])
                self.assertIn('components', enhanced_analysis[metric])
                self.assertGreaterEqual(enhanced_analysis[metric]['score'], 0)
                self.assertLessEqual(enhanced_analysis[metric]['score'], 100)
        
        # Check gaps metric (has different structure)
        gaps_metric = enhanced_analysis['gaps']
        self.assertIn('score', gaps_metric)
        self.assertIn('identified_gaps', gaps_metric)
        self.assertIn('improvement_suggestions', gaps_metric)
        self.assertGreaterEqual(gaps_metric['score'], 0)
        self.assertLessEqual(gaps_metric['score'], 100)
    
    def test_enhanced_scoring_without_job_description(self):
        """Test enhanced scoring in quality-check mode (no job description)."""
        enhanced_analysis = get_enhanced_resume_score(self.sample_resume_text, None)
        
        # Relevance should be None when no job description provided
        self.assertIsNone(enhanced_analysis['relevance']['score'])
        
        # Other metrics should still work
        self.assertIsNotNone(enhanced_analysis['impact']['score'])
        self.assertIsNotNone(enhanced_analysis['structure']['score'])
        self.assertIsNotNone(enhanced_analysis['clarity']['score'])
        self.assertIsNotNone(enhanced_analysis['gaps']['score'])
    
    def test_backward_compatibility(self):
        """Test that enhanced system maintains backward compatibility."""
        # Test legacy format option
        legacy_format = get_enhanced_resume_score(self.sample_resume_text, self.job_description, legacy_format=True)
        direct_legacy = get_resume_quality_score(self.sample_resume_text)
        
        # Should have same structure as direct legacy call
        self.assertIn('overall_score', legacy_format)
        self.assertIn('action_verb_analysis', legacy_format)
        self.assertIn('quantifiable_score', legacy_format)
        self.assertIn('conciseness_score', legacy_format)
    
    def test_similarity_calculation(self):
        """Test semantic similarity calculation."""
        similarity = calculate_similarity(self.sample_resume_text, self.job_description)
        
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
    
    def test_keyword_analysis(self):
        """Test keyword matching analysis."""
        skills = parser.extract_skills(self.sample_resume_text)
        matched, missing = analyze_keywords(skills, self.job_description)
        
        self.assertIsInstance(matched, list)
        self.assertIsInstance(missing, list)
        
        # Should find some matches given our sample data
        self.assertGreater(len(matched + missing), 0)


if __name__ == '__main__':
    unittest.main()

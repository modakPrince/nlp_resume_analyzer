"""
Test cases for the Resume Analyzer
"""

import unittest
import os
import tempfile
from src.nlp_engine.resume_analyzer import ResumeAnalyzer


class TestResumeAnalyzer(unittest.TestCase):
    """Test cases for the main ResumeAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ResumeAnalyzer()
        
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
    
    def test_analyze_valid_resume(self):
        """Test analysis with valid resume content."""
        # This is a basic test - in a real scenario, you'd create actual PDF/DOCX files
        # For now, we'll test the individual components
        
        # Test information extraction
        extracted_info = self.analyzer.extractor.extract_information(self.sample_resume_text)
        
        self.assertIsNotNone(extracted_info['name'])
        self.assertIn('@', extracted_info['email'] or '')
        self.assertTrue(len(extracted_info['skills']) > 0)
    
    def test_job_fit_analysis(self):
        """Test job fit analysis functionality."""
        analysis = self.analyzer.analyzer.analyze_fit(self.sample_resume_text, self.job_description)
        
        self.assertIn('semantic_similarity', analysis)
        self.assertIn('keyword_analysis', analysis)
        self.assertIn('farming_detection', analysis)
        self.assertIn('readability', analysis)
        self.assertIn('final_score', analysis)
        
        # Check that final score is between 0 and 1
        self.assertGreaterEqual(analysis['final_score'], 0.0)
        self.assertLessEqual(analysis['final_score'], 1.0)
    
    def test_keyword_farming_detection(self):
        """Test keyword farming detection."""
        # Create a resume with obvious keyword stuffing
        farming_resume = """
        John Doe
        john@email.com
        
        Skills: Python Python Python Java Java SQL SQL SQL React React
        Python JavaScript Python SQL Python React Python Docker
        AWS Python Kubernetes Python Git Python Agile Python
        """
        
        farming_analysis = self.analyzer.analyzer._detect_keyword_farming(farming_resume)
        
        # Should detect high farming risk
        self.assertGreater(farming_analysis['farming_score'], 0.5)
    
    def test_readability_analysis(self):
        """Test readability analysis."""
        readability = self.analyzer.analyzer._analyze_readability(self.sample_resume_text)
        
        self.assertIn('flesch_reading_ease', readability)
        self.assertIn('quality', readability)
        self.assertIn('concern_level', readability)


if __name__ == '__main__':
    unittest.main()

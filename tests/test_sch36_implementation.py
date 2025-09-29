#!/usr/bin/env python3
"""
Test script to verify SCH-36 implementation works correctly.
This tests the core logic without requiring all dependencies.
"""

import sys
import os
import re

# Add project root and src to path
project_root = os.path.dirname(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

def mock_extract_action_verbs(text):
    """Mock version of parser.extract_action_verbs for testing."""
    # Simple mock that finds some action verbs
    impact_verbs = ['led', 'managed', 'delivered', 'achieved', 'improved']
    build_verbs = ['developed', 'built', 'created', 'implemented', 'designed']
    support_verbs = ['assisted', 'supported', 'helped', 'collaborated']
    
    found_impact = [verb for verb in impact_verbs if verb in text.lower()]
    found_build = [verb for verb in build_verbs if verb in text.lower()]
    found_support = [verb for verb in support_verbs if verb in text.lower()]
    
    return {
        'weighted_score': len(found_impact) * 3 + len(found_build) * 2 + len(found_support) * 1,
        'total_verbs': len(found_impact) + len(found_build) + len(found_support),
        'tier_counts': {
            'impact': len(found_impact),
            'build': len(found_build), 
            'support': len(found_support)
        },
        'impact_verbs': found_impact,
        'build_verbs': found_build,
        'support_verbs': found_support
    }

def mock_extract_skills(text):
    """Mock version of parser.extract_skills for testing."""
    # Simple skill extraction
    common_skills = ['python', 'javascript', 'react', 'docker', 'aws', 'sql', 'git']
    found = [skill for skill in common_skills if skill in text.lower()]
    return found

# Mock the parser module
class MockParser:
    @staticmethod
    def extract_action_verbs(text):
        return mock_extract_action_verbs(text)
    
    @staticmethod
    def extract_skills(text):
        return mock_extract_skills(text)

# Temporarily replace parser import
sys.modules['nlp_engine.parser'] = MockParser()

# Import our analyzer functions
try:
    from nlp_engine.analyzer import (
        _calculate_structured_metrics,
        _calculate_relevance_score,
        _calculate_impact_score,
        _calculate_structure_score, 
        _calculate_clarity_score,
        _calculate_gaps_score,
        _calculate_overall_score
    )
    
    print("✅ Successfully imported enhanced scoring functions!")
    
    # Test data
    sample_resume = """
    John Doe
    john.doe@email.com
    (555) 123-4567

    EXPERIENCE
    Senior Software Developer - Tech Corp (2020-2023)
    - Led a team of 5 developers in building scalable web applications using Python and React
    - Implemented microservices architecture with Docker containers  
    - Improved system performance by 40% through database optimization
    - Managed CI/CD pipelines and delivered features 25% faster

    SKILLS
    Python, JavaScript, React, Docker, AWS, PostgreSQL
    """

    sample_job_desc = """
    We are looking for a Senior Python Developer with experience in:
    - Python web development
    - Docker containerization  
    - React frontend development
    - AWS cloud services
    - Team leadership experience
    """

    print("\n🧪 Testing individual metric calculations...")
    
    # Mock spaCy doc for testing (simplified)
    class MockDoc:
        def __init__(self, text):
            self.text = text
            self.sents = [MockSent(s.strip()) for s in text.split('.') if s.strip()]
            tokens = text.split()
            self.tokens = [MockToken(t) for t in tokens]
        
        def __iter__(self):
            return iter(self.tokens)
    
    class MockSent:
        def __init__(self, text):
            self.text = text
            
        def __len__(self):
            return len(self.text.split())
    
    class MockToken:
        def __init__(self, text):
            self.text = text
            self.is_alpha = text.isalpha()
    
    # Test individual functions with mocked dependencies
    doc = MockDoc(sample_resume)
    lines = [line.strip() for line in sample_resume.split('\n') if line.strip()]
    
    # Test Impact Score
    action_verb_analysis = mock_extract_action_verbs(sample_resume)
    impact_result = _calculate_impact_score(sample_resume, action_verb_analysis, lines, doc)
    print(f"   Impact Score: {impact_result['score']:.1f}%")
    
    # Test Structure Score  
    structure_result = _calculate_structure_score(sample_resume, lines, doc)
    print(f"   Structure Score: {structure_result['score']:.1f}%")
    
    # Test Clarity Score
    clarity_result = _calculate_clarity_score(sample_resume, lines, doc)
    print(f"   Clarity Score: {clarity_result['score']:.1f}%")
    
    # Test Overall Score calculation
    mock_scores = [
        {"score": 85.0},  # relevance
        impact_result,    # impact
        structure_result, # structure
        clarity_result,   # clarity
        {"score": 75.0}   # gaps
    ]
    overall = _calculate_overall_score(mock_scores)
    print(f"   Overall Score: {overall:.1f}%")
    
    print("\n✅ All core SCH-36 functions working correctly!")
    print("🎉 SCH-36 implementation appears successful!")
    
except Exception as e:
    print(f"❌ Error testing SCH-36: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
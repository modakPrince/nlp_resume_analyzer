"""
Test cases for SCH-30: Weighted Action Verb Tiers Scoring
"""

import unittest
import sys
import os

# Add src to path for importing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from nlp_engine.parser import extract_action_verbs
from nlp_engine.analyzer import get_resume_quality_score


class TestActionVerbScoring(unittest.TestCase):
    """Test cases for weighted action verb scoring functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        
        # Sample resume with different action verb tiers
        self.sample_resume_impact = """
        John Doe
        john.doe@email.com
        
        EXPERIENCE
        Senior Software Developer - Tech Corp (2020-2023)
        • Led a team of 5 developers in building scalable applications
        • Managed project delivery across multiple cross-functional teams  
        • Pioneered adoption of microservices architecture
        • Achieved 40% improvement in system performance
        • Spearheaded migration to cloud infrastructure
        """
        
        self.sample_resume_build = """
        Jane Smith
        jane.smith@email.com
        
        EXPERIENCE  
        Software Engineer - StartupCo (2019-2022)
        • Developed RESTful APIs using Python and Flask
        • Built responsive web applications with React
        • Created automated testing framework
        • Implemented CI/CD pipeline using Jenkins
        • Designed scalable database architecture
        """
        
        self.sample_resume_support = """
        Bob Johnson
        bob.johnson@email.com
        
        EXPERIENCE
        Junior Developer - WebCorp (2018-2021)
        • Assisted senior developers with feature implementation
        • Helped troubleshoot production issues
        • Collaborated with QA team on testing procedures
        • Supported deployment activities
        • Participated in code review sessions
        """
        
        self.sample_resume_mixed = """
        Alice Chen
        alice.chen@email.com
        
        EXPERIENCE
        Tech Lead - InnovaCorp (2020-2023)
        • Led cross-functional team of 8 engineers
        • Developed microservices architecture for payment system
        • Assisted in hiring and onboarding new developers
        • Built automated deployment pipeline
        • Managed stakeholder communications and project planning
        • Collaborated with product team on feature prioritization
        """
    
    def test_extract_action_verbs_impact_heavy(self):
        """Test extraction with impact-heavy resume."""
        result = extract_action_verbs(self.sample_resume_impact)
        
        # Should find multiple impact verbs
        self.assertGreater(result['tier_counts']['impact'], 0)
        self.assertIn('led', result['impact_verbs'])
        self.assertIn('managed', result['impact_verbs'])
        
        # Should have high weighted score due to impact verbs (3x weight)
        self.assertGreater(result['weighted_score'], 10.0)
    
    def test_extract_action_verbs_build_heavy(self):
        """Test extraction with build-heavy resume.""" 
        result = extract_action_verbs(self.sample_resume_build)
        
        # Should find multiple build verbs
        self.assertGreater(result['tier_counts']['build'], 0)
        self.assertIn('developed', result['build_verbs'])
        self.assertIn('built', result['build_verbs'])
        
        # Should have moderate weighted score due to build verbs (2x weight)
        self.assertGreater(result['weighted_score'], 5.0)
        self.assertLess(result['weighted_score'], 15.0)
    
    def test_extract_action_verbs_support_heavy(self):
        """Test extraction with support-heavy resume."""
        result = extract_action_verbs(self.sample_resume_support)
        
        # Should find multiple support verbs
        self.assertGreater(result['tier_counts']['support'], 0)
        self.assertIn('assisted', result['support_verbs'])
        self.assertIn('helped', result['support_verbs'])
        
        # Should have lower weighted score due to support verbs (1x weight)
        self.assertGreater(result['weighted_score'], 0.0)
        self.assertLess(result['weighted_score'], 10.0)
    
    def test_extract_action_verbs_mixed_resume(self):
        """Test extraction with mixed verb tiers."""
        result = extract_action_verbs(self.sample_resume_mixed)
        
        # Should find verbs from all tiers
        self.assertGreater(result['tier_counts']['impact'], 0)
        self.assertGreater(result['tier_counts']['build'], 0)
        self.assertGreater(result['tier_counts']['support'], 0)
        
        # Total verbs should equal sum of tier counts
        expected_total = (result['tier_counts']['impact'] + 
                         result['tier_counts']['build'] + 
                         result['tier_counts']['support'])
        self.assertEqual(result['total_verbs'], expected_total)
        
        # Weighted score should be calculated correctly
        expected_score = (result['tier_counts']['impact'] * 3.0 + 
                         result['tier_counts']['build'] * 2.0 + 
                         result['tier_counts']['support'] * 1.0)
        self.assertEqual(result['weighted_score'], expected_score)
    
    def test_get_resume_quality_score_structure(self):
        """Test that quality score returns proper structure."""
        result = get_resume_quality_score(self.sample_resume_mixed)
        
        # Should return dict with expected keys
        expected_keys = ['overall_score', 'action_verb_analysis', 'quantifiable_score', 
                        'conciseness_score', 'breakdown']
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Overall score should be between 0 and 100
        self.assertGreaterEqual(result['overall_score'], 0.0)
        self.assertLessEqual(result['overall_score'], 100.0)
        
        # Action verb analysis should contain expected structure
        verb_analysis = result['action_verb_analysis']
        self.assertIn('tier_counts', verb_analysis)
        self.assertIn('weighted_score', verb_analysis)
        self.assertIn('total_verbs', verb_analysis)
    
    def test_verb_tier_weights(self):
        """Test that verb tiers have correct weight multipliers."""
        # Create test resumes with exactly one verb from each tier
        impact_resume = "• Led the team to success"
        build_resume = "• Developed the application" 
        support_resume = "• Assisted the team"
        
        impact_result = extract_action_verbs(impact_resume)
        build_result = extract_action_verbs(build_resume)
        support_result = extract_action_verbs(support_resume)
        
        # Verify weight ratios
        self.assertEqual(impact_result['weighted_score'], 3.0)
        self.assertEqual(build_result['weighted_score'], 2.0) 
        self.assertEqual(support_result['weighted_score'], 1.0)
    
    def test_empty_resume(self):
        """Test handling of empty or minimal resume."""
        empty_result = extract_action_verbs("")
        
        # Should return zero counts for empty resume
        self.assertEqual(empty_result['total_verbs'], 0)
        self.assertEqual(empty_result['weighted_score'], 0.0)
        self.assertEqual(empty_result['tier_counts']['impact'], 0)
        self.assertEqual(empty_result['tier_counts']['build'], 0)
        self.assertEqual(empty_result['tier_counts']['support'], 0)


if __name__ == '__main__':
    unittest.main()
"""
Core NLP Resume Analyzer Package
Contains the main processing logic for resume analysis.
"""

__version__ = "1.1.0"
__author__ = "Your Name"

from . import parser  # re-export parser module
from .analyzer import (
    calculate_similarity,
    get_resume_quality_score,
    analyze_keywords,
)

__all__ = [
    "parser",
    "calculate_similarity",
    "get_resume_quality_score",
    "analyze_keywords",
]


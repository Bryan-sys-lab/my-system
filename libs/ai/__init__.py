"""
B-Search AI Module

This module provides AI-powered analytics, reporting, and intelligence capabilities
for the B-Search platform.

Modules:
- ai_analyzer: Core AI analysis engine
- report_generator: Multi-format report generation
- narrative_generator: Intelligent narrative creation
- content_summarizer: AI-powered content summarization
- statistical_analyzer: Statistical analysis functions

Usage:
    from libs.ai import AIAnalyzer, ReportGenerator, NarrativeGenerator
    from libs.ai.statistical_analyzer import analyze_trends, detect_anomalies
"""

__version__ = "1.0.0"
__author__ = "B-Search AI Team"

# Import main classes for easy access
from .ai_analyzer import AIAnalyzer
from .report_generator import ReportGenerator
from .narrative_generator import NarrativeGenerator
from .content_summarizer import ContentSummarizer

__all__ = [
    'AIAnalyzer',
    'ReportGenerator',
    'NarrativeGenerator',
    'ContentSummarizer',
    '__version__',
    '__author__'
]
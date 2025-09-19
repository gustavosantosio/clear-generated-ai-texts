"""
Clear Generated AI Texts - A tool to detect and clear AI-generated text content.

This package provides functionality to identify and remove AI-generated text
from various sources, helping maintain content authenticity.
"""

__version__ = "0.1.0"
__author__ = "Gustavo Santos"
__email__ = "gustavo@example.com"

from .detector import AITextDetector
from .cleaner import TextCleaner

__all__ = ["AITextDetector", "TextCleaner"]
"""
Text Cleaner Module

This module provides functionality to clean and remove AI-generated text
from various sources while preserving human-generated content.
"""

from typing import Dict, List, Optional, Union
import re
from .detector import AITextDetector


class TextCleaner:
    """
    A class to clean and remove AI-generated text content.
    
    This cleaner can identify and remove AI-generated text while preserving
    human-generated content based on detection results.
    """
    
    def __init__(self, detector: Optional[AITextDetector] = None):
        """
        Initialize the text cleaner.
        
        Args:
            detector: Optional AITextDetector instance. If None, creates a new one.
        """
        self.detector = detector or AITextDetector()
        self.removal_strategy = "complete"  # "complete", "partial", "mark"
    
    def clean_text(self, text: str, strategy: Optional[str] = None) -> Dict[str, Union[str, bool, float]]:
        """
        Clean the given text by removing AI-generated content.
        
        Args:
            text (str): The text to clean
            strategy (str, optional): Cleaning strategy ("complete", "partial", "mark")
            
        Returns:
            Dict containing:
                - cleaned_text: The cleaned text
                - was_modified: Boolean indicating if text was modified
                - confidence: Confidence level of AI detection
        """
        if not text or not isinstance(text, str):
            return {
                "cleaned_text": text or "",
                "was_modified": False,
                "confidence": 0.0
            }
        
        strategy = strategy or self.removal_strategy
        detection_result = self.detector.detect(text)
        
        # Only skip cleaning if there are no matches and very low confidence
        if not detection_result["matches"] and detection_result["confidence"] < 0.3:
            return {
                "cleaned_text": text,
                "was_modified": False,
                "confidence": detection_result["confidence"]
            }
        
        # Apply cleaning strategy
        if strategy == "complete":
            cleaned_text = self._remove_completely(text, detection_result)
        elif strategy == "partial":
            cleaned_text = self._remove_partial(text, detection_result)
        elif strategy == "mark":
            cleaned_text = self._mark_ai_content(text, detection_result)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        return {
            "cleaned_text": cleaned_text,
            "was_modified": cleaned_text != text,
            "confidence": detection_result["confidence"]
        }
    
    def clean_lines(self, lines: List[str], strategy: Optional[str] = None) -> Dict[str, Union[List[str], int, float]]:
        """
        Clean a list of text lines by removing AI-generated content.
        
        Args:
            lines (List[str]): List of text lines to clean
            strategy (str, optional): Cleaning strategy
            
        Returns:
            Dict containing:
                - cleaned_lines: List of cleaned text lines
                - removed_count: Number of lines removed
                - avg_confidence: Average confidence of AI detection
        """
        if not lines:
            return {
                "cleaned_lines": [],
                "removed_count": 0,
                "avg_confidence": 0.0
            }
        
        strategy = strategy or self.removal_strategy
        cleaned_lines = []
        removed_count = 0
        total_confidence = 0.0
        
        for line in lines:
            result = self.clean_text(line, strategy)
            
            if strategy == "complete" and result["was_modified"] and not result["cleaned_text"].strip():
                removed_count += 1
            else:
                cleaned_lines.append(result["cleaned_text"])
            
            total_confidence += result["confidence"]
        
        avg_confidence = total_confidence / len(lines) if lines else 0.0
        
        return {
            "cleaned_lines": cleaned_lines,
            "removed_count": removed_count,
            "avg_confidence": avg_confidence
        }
    
    def _remove_completely(self, text: str, detection_result: Dict) -> str:
        """Remove AI-generated text completely."""
        if detection_result["confidence"] > 0.8:
            return ""
        
        # For lower confidence, try to remove specific AI patterns
        cleaned_text = text
        for pattern in detection_result["matches"]:
            # Remove sentences containing AI patterns
            sentences = re.split(r'([.!?]+)', cleaned_text)
            filtered_sentences = []
            
            for i in range(0, len(sentences), 2):
                if i < len(sentences):
                    sentence = sentences[i]
                    punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
                    
                    if not re.search(pattern, sentence, re.IGNORECASE):
                        filtered_sentences.extend([sentence, punctuation])
            
            cleaned_text = "".join(filtered_sentences)
        
        return cleaned_text.strip()
    
    def _remove_partial(self, text: str, detection_result: Dict) -> str:
        """Remove only the most obvious AI-generated parts."""
        cleaned_text = text
        
        # Remove specific AI phrases based on matched patterns
        if detection_result["matches"]:
            for pattern in detection_result["matches"]:
                # Convert the regex pattern to a more comprehensive removal pattern
                if "as an ai" in pattern.lower():
                    cleaned_text = re.sub(r"as an ai[^.!?]*[.!?]\s*", "", cleaned_text, flags=re.IGNORECASE)
                elif "i(?:'m| am) an ai" in pattern.lower():
                    cleaned_text = re.sub(r"i(?:'m| am) an ai[^.!?]*[.!?]\s*", "", cleaned_text, flags=re.IGNORECASE)
                elif "don't have personal experiences" in pattern.lower():
                    cleaned_text = re.sub(r"i don't have personal experiences[^.!?]*[.!?]\s*", "", cleaned_text, flags=re.IGNORECASE)
                elif "can't provide personal opinions" in pattern.lower():
                    cleaned_text = re.sub(r"i can't provide personal opinions[^.!?]*[.!?]\s*", "", cleaned_text, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text
    
    def _mark_ai_content(self, text: str, detection_result: Dict) -> str:
        """Mark AI-generated content instead of removing it."""
        if detection_result["confidence"] > 0.8:
            return f"[AI-GENERATED: {detection_result['confidence']:.2f}] {text}"
        
        marked_text = text
        if detection_result["matches"]:
            for pattern in detection_result["matches"]:
                # Mark based on the actual matched patterns
                if "as an ai" in pattern.lower():
                    marked_text = re.sub(
                        r"(as an ai(?:\s+language)?\s+model)",
                        r"[AI-PATTERN] \1",
                        marked_text,
                        flags=re.IGNORECASE
                    )
                elif "i(?:'m| am) an ai" in pattern.lower():
                    marked_text = re.sub(
                        r"(i(?:'m| am) an ai)",
                        r"[AI-PATTERN] \1",
                        marked_text,
                        flags=re.IGNORECASE
                    )
                else:
                    # Fallback to original pattern matching
                    marked_text = re.sub(
                        pattern,
                        f"[AI-PATTERN] \\g<0>",
                        marked_text,
                        flags=re.IGNORECASE
                    )
        
        return marked_text
    
    def set_removal_strategy(self, strategy: str) -> None:
        """
        Set the default removal strategy.
        
        Args:
            strategy (str): Strategy ("complete", "partial", "mark")
        """
        valid_strategies = ["complete", "partial", "mark"]
        if strategy not in valid_strategies:
            raise ValueError(f"Strategy must be one of: {valid_strategies}")
        
        self.removal_strategy = strategy
"""
Tests for the AI Text Detector module.
"""

import pytest
from clear_generated_ai_texts.detector import AITextDetector


class TestAITextDetector:
    """Test cases for the AITextDetector class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.detector = AITextDetector()
    
    def test_init(self):
        """Test detector initialization."""
        assert isinstance(self.detector.ai_patterns, list)
        assert len(self.detector.ai_patterns) > 0
        assert self.detector.confidence_threshold == 0.7
    
    def test_detect_empty_text(self):
        """Test detection with empty or None text."""
        result = self.detector.detect("")
        assert result["is_ai_generated"] is False
        assert result["confidence"] == 0.0
        assert result["matches"] == []
        
        result = self.detector.detect(None)
        assert result["is_ai_generated"] is False
        assert result["confidence"] == 0.0
        assert result["matches"] == []
    
    def test_detect_human_text(self):
        """Test detection with clearly human text."""
        human_text = "I went to the store yesterday and bought some groceries. The weather was nice."
        result = self.detector.detect(human_text)
        
        assert result["is_ai_generated"] is False
        assert result["confidence"] < 0.7
        assert len(result["matches"]) == 0
    
    def test_detect_ai_text(self):
        """Test detection with clearly AI-generated text."""
        ai_text = "As an AI language model, I don't have personal experiences or feelings."
        result = self.detector.detect(ai_text)
        
        assert result["is_ai_generated"] is True
        assert result["confidence"] >= 0.7
        assert len(result["matches"]) > 0
    
    def test_detect_partial_ai_text(self):
        """Test detection with text containing some AI patterns."""
        partial_ai_text = "I understand you're looking for information. Here are some facts about cats."
        result = self.detector.detect(partial_ai_text)
        
        assert isinstance(result["is_ai_generated"], bool)
        assert 0 <= result["confidence"] <= 1.0
        assert isinstance(result["matches"], list)
    
    def test_set_confidence_threshold(self):
        """Test setting confidence threshold."""
        self.detector.set_confidence_threshold(0.5)
        assert self.detector.confidence_threshold == 0.5
        
        self.detector.set_confidence_threshold(0.9)
        assert self.detector.confidence_threshold == 0.9
        
        # Test invalid threshold
        with pytest.raises(ValueError):
            self.detector.set_confidence_threshold(1.5)
        
        with pytest.raises(ValueError):
            self.detector.set_confidence_threshold(-0.1)
    
    def test_add_pattern(self):
        """Test adding custom patterns."""
        initial_count = len(self.detector.ai_patterns)
        
        self.detector.add_pattern("custom pattern")
        assert len(self.detector.ai_patterns) == initial_count + 1
        assert "custom pattern" in self.detector.ai_patterns
        
        # Test adding duplicate pattern
        self.detector.add_pattern("custom pattern")
        assert len(self.detector.ai_patterns) == initial_count + 1
    
    def test_formal_structure_detection(self):
        """Test detection of formal structure patterns."""
        formal_text = "First, we need to consider the options. Second, we should analyze the data. In conclusion, this is important."
        result = self.detector.detect(formal_text)
        
        # Should have some confidence due to formal structure
        assert result["confidence"] > 0.0
    
    def test_case_insensitive_detection(self):
        """Test that detection is case-insensitive."""
        text_lower = "as an ai language model, i can help you."
        text_upper = "AS AN AI LANGUAGE MODEL, I CAN HELP YOU."
        text_mixed = "As An AI Language Model, I Can Help You."
        
        result_lower = self.detector.detect(text_lower)
        result_upper = self.detector.detect(text_upper)
        result_mixed = self.detector.detect(text_mixed)
        
        assert result_lower["is_ai_generated"] == result_upper["is_ai_generated"]
        assert result_lower["is_ai_generated"] == result_mixed["is_ai_generated"]
        assert len(result_lower["matches"]) == len(result_upper["matches"])
        assert len(result_lower["matches"]) == len(result_mixed["matches"])
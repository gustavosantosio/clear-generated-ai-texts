"""
Tests for the Text Cleaner module.
"""

import pytest
from clear_generated_ai_texts.detector import AITextDetector
from clear_generated_ai_texts.cleaner import TextCleaner


class TestTextCleaner:
    """Test cases for the TextCleaner class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.detector = AITextDetector()
        self.cleaner = TextCleaner(self.detector)
    
    def test_init(self):
        """Test cleaner initialization."""
        assert isinstance(self.cleaner.detector, AITextDetector)
        assert self.cleaner.removal_strategy == "complete"
        
        # Test with no detector provided
        cleaner2 = TextCleaner()
        assert isinstance(cleaner2.detector, AITextDetector)
    
    def test_clean_empty_text(self):
        """Test cleaning empty or None text."""
        result = self.cleaner.clean_text("")
        assert result["cleaned_text"] == ""
        assert result["was_modified"] is False
        assert result["confidence"] == 0.0
        
        result = self.cleaner.clean_text(None)
        assert result["cleaned_text"] == ""
        assert result["was_modified"] is False
        assert result["confidence"] == 0.0
    
    def test_clean_human_text(self):
        """Test cleaning human text (should remain unchanged)."""
        human_text = "I went to the store yesterday and bought some groceries."
        result = self.cleaner.clean_text(human_text)
        
        assert result["cleaned_text"] == human_text
        assert result["was_modified"] is False
        assert result["confidence"] < 0.7
    
    def test_clean_ai_text_complete(self):
        """Test cleaning AI text with complete removal strategy."""
        ai_text = "As an AI language model, I don't have personal experiences."
        result = self.cleaner.clean_text(ai_text, "complete")
        
        assert result["was_modified"] is True
        assert result["confidence"] >= 0.7
        # Should be significantly reduced or empty
        assert len(result["cleaned_text"]) < len(ai_text)
    
    def test_clean_ai_text_partial(self):
        """Test cleaning AI text with partial removal strategy."""
        ai_text = "As an AI language model, I can help you with information. Cats are mammals."
        result = self.cleaner.clean_text(ai_text, "partial")
        
        assert result["was_modified"] is True
        # Should still contain some content (the factual part)
        assert len(result["cleaned_text"]) > 0
        # Should not contain AI identification phrases
        assert "as an ai" not in result["cleaned_text"].lower()
    
    def test_clean_ai_text_mark(self):
        """Test cleaning AI text with mark strategy."""
        ai_text = "As an AI language model, I can help you."
        result = self.cleaner.clean_text(ai_text, "mark")
        
        assert result["was_modified"] is True
        # Original text should still be present
        assert ai_text in result["cleaned_text"] or "[AI-" in result["cleaned_text"]
    
    def test_clean_lines(self):
        """Test cleaning multiple lines of text."""
        lines = [
            "This is human text.",
            "As an AI language model, I don't have feelings.",
            "Another human sentence.",
            "I'm an AI assistant and I can help you."
        ]
        
        result = self.cleaner.clean_lines(lines, "complete")
        
        assert "cleaned_lines" in result
        assert "removed_count" in result
        assert "avg_confidence" in result
        assert result["removed_count"] >= 0
        assert 0 <= result["avg_confidence"] <= 1.0
    
    def test_set_removal_strategy(self):
        """Test setting removal strategy."""
        self.cleaner.set_removal_strategy("partial")
        assert self.cleaner.removal_strategy == "partial"
        
        self.cleaner.set_removal_strategy("mark")
        assert self.cleaner.removal_strategy == "mark"
        
        # Test invalid strategy
        with pytest.raises(ValueError):
            self.cleaner.set_removal_strategy("invalid")
    
    def test_mixed_content(self):
        """Test cleaning text with mixed human and AI content."""
        mixed_text = """
        This is a regular paragraph about cats. Cats are interesting animals.
        
        As an AI language model, I don't have personal experiences with pets.
        
        But here are some facts about cats that might interest you.
        """
        
        result = self.cleaner.clean_text(mixed_text, "partial")
        
        # Should preserve the factual content while removing AI identification
        assert "cats" in result["cleaned_text"].lower()
        assert "facts" in result["cleaned_text"].lower()
        # Should remove or reduce AI identification
        assert result["cleaned_text"] != mixed_text  # Should be modified
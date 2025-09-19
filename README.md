# Clear Generated AI Texts

A Python tool to detect and remove AI-generated text content, helping maintain content authenticity and human-written quality.

## Features

- **AI Text Detection**: Identify AI-generated content using pattern matching and heuristics
- **Multiple Cleaning Strategies**: Choose from complete removal, partial cleaning, or content marking
- **CLI Interface**: Easy-to-use command-line tools for batch processing
- **File Processing**: Clean individual files or entire directories
- **Configurable Thresholds**: Adjust detection sensitivity based on your needs
- **Backup Support**: Automatically backup original files before cleaning

## Installation

### From Source

```bash
git clone https://github.com/gustavosantosio/clear-generated-ai-texts.git
cd clear-generated-ai-texts
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/gustavosantosio/clear-generated-ai-texts.git
cd clear-generated-ai-texts
pip install -e ".[dev]"
```

## Quick Start

### Command Line Usage

#### Detect AI Content

```bash
# Detect AI content in text
clear-ai-texts detect "As an AI language model, I can help you with information."

# Use custom threshold
clear-ai-texts detect "Your text here" --threshold 0.8

# JSON output
clear-ai-texts detect "Your text here" --output json
```

#### Clean AI Content

```bash
# Clean text with default settings
clear-ai-texts clean "As an AI language model, I can help you. Cats are mammals."

# Use different cleaning strategies
clear-ai-texts clean "Your text" --strategy partial
clear-ai-texts clean "Your text" --strategy mark

# JSON output
clear-ai-texts clean "Your text" --output json
```

#### Process Files

```bash
# Clean a single file
clear-ai-texts clean-file input.txt --backup

# Clean with custom output file
clear-ai-texts clean-file input.txt --output-file cleaned.txt

# Clean entire directory
clear-ai-texts clean-directory ./texts/ --pattern "*.txt" --backup

# Dry run to see what would be changed
clear-ai-texts clean-directory ./texts/ --dry-run
```

### Python API Usage

#### Basic Detection

```python
from clear_generated_ai_texts import AITextDetector

detector = AITextDetector()
result = detector.detect("As an AI language model, I can help you.")

print(f"AI-generated: {result['is_ai_generated']}")
print(f"Confidence: {result['confidence']:.2f}")
print(f"Patterns matched: {len(result['matches'])}")
```

#### Text Cleaning

```python
from clear_generated_ai_texts import AITextDetector, TextCleaner

detector = AITextDetector()
cleaner = TextCleaner(detector)

# Clean text with different strategies
result = cleaner.clean_text(
    "As an AI, I don't have feelings. But cats are great pets!",
    strategy="partial"
)

print(f"Original was modified: {result['was_modified']}")
print(f"Cleaned text: {result['cleaned_text']}")
```

#### Custom Configuration

```python
from clear_generated_ai_texts import AITextDetector, TextCleaner

# Create detector with custom threshold
detector = AITextDetector()
detector.set_confidence_threshold(0.8)

# Add custom patterns
detector.add_pattern(r"i am an artificial intelligence")

# Create cleaner with custom strategy
cleaner = TextCleaner(detector)
cleaner.set_removal_strategy("partial")

# Process text
result = cleaner.clean_text("Your text here")
```

## Cleaning Strategies

### Complete Removal
- **Description**: Removes entire sentences or paragraphs containing AI patterns
- **Use Case**: When you want to eliminate all traces of AI-generated content
- **Command**: `--strategy complete`

### Partial Removal
- **Description**: Removes only the specific AI identification phrases while preserving factual content
- **Use Case**: When AI-generated text contains useful information you want to keep
- **Command**: `--strategy partial`

### Content Marking
- **Description**: Marks AI-generated content with labels instead of removing it
- **Use Case**: For review purposes or when you want to identify but not remove content
- **Command**: `--strategy mark`

## Configuration

### Detection Threshold

The confidence threshold determines how sensitive the AI detection is:

- **0.1-0.3**: Very sensitive, may flag human text with formal language
- **0.4-0.6**: Moderate sensitivity, good for mixed content
- **0.7-0.9**: Conservative, only flags obvious AI patterns (default: 0.7)
- **0.9-1.0**: Very conservative, only flags extremely obvious cases

### Custom Patterns

You can add custom detection patterns for specific AI models or phrases:

```python
detector = AITextDetector()
detector.add_pattern(r"according to my training data")
detector.add_pattern(r"i was created by")
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=clear_generated_ai_texts --cov-report=html

# Run specific test file
pytest tests/test_detector.py
```

### Code Quality

```bash
# Format code
black clear_generated_ai_texts/ tests/

# Lint code
flake8 clear_generated_ai_texts/ tests/

# Type checking
mypy clear_generated_ai_texts/
```

### Project Structure

```
clear-generated-ai-texts/
├── clear_generated_ai_texts/
│   ├── __init__.py
│   ├── detector.py          # AI detection logic
│   ├── cleaner.py           # Text cleaning logic
│   └── cli.py              # Command-line interface
├── tests/
│   ├── __init__.py
│   ├── test_detector.py
│   └── test_cleaner.py
├── pyproject.toml          # Project configuration
├── README.md
├── LICENSE
└── .gitignore
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting PRs

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the need to maintain content authenticity in an AI-driven world
- Built with modern Python packaging and development practices

## Disclaimer

This tool uses heuristic-based detection and may not catch all AI-generated content or may occasionally flag human-written text. It should be used as part of a comprehensive content review process, not as the sole method of detection.
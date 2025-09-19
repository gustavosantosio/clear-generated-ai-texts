"""
Command Line Interface for Clear Generated AI Texts

This module provides a CLI interface for detecting and cleaning AI-generated text.
"""

import sys
import json
from pathlib import Path
from typing import Optional

import click

from .detector import AITextDetector
from .cleaner import TextCleaner


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Clear Generated AI Texts - Detect and remove AI-generated text content."""
    pass


@cli.command()
@click.argument('text')
@click.option('--threshold', '-t', default=0.7, type=float, 
              help='Confidence threshold for AI detection (0.0-1.0)')
@click.option('--output', '-o', type=click.Choice(['json', 'text']), default='text',
              help='Output format')
def detect(text: str, threshold: float, output: str):
    """Detect if the given text is AI-generated."""
    detector = AITextDetector()
    detector.set_confidence_threshold(threshold)
    
    result = detector.detect(text)
    
    if output == 'json':
        click.echo(json.dumps(result, indent=2))
    else:
        is_ai = "Yes" if result["is_ai_generated"] else "No"
        click.echo(f"AI-generated: {is_ai}")
        click.echo(f"Confidence: {result['confidence']:.2f}")
        if result["matches"]:
            click.echo(f"Matches: {len(result['matches'])} patterns")


@cli.command()
@click.argument('text')
@click.option('--strategy', '-s', type=click.Choice(['complete', 'partial', 'mark']), 
              default='complete', help='Cleaning strategy')
@click.option('--threshold', '-t', default=0.7, type=float,
              help='Confidence threshold for AI detection (0.0-1.0)')
@click.option('--output', '-o', type=click.Choice(['json', 'text']), default='text',
              help='Output format')
def clean(text: str, strategy: str, threshold: float, output: str):
    """Clean AI-generated content from the given text."""
    detector = AITextDetector()
    detector.set_confidence_threshold(threshold)
    
    cleaner = TextCleaner(detector)
    result = cleaner.clean_text(text, strategy)
    
    if output == 'json':
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo("Cleaned text:")
        click.echo(result["cleaned_text"])
        click.echo(f"\nModified: {'Yes' if result['was_modified'] else 'No'}")
        click.echo(f"Confidence: {result['confidence']:.2f}")


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output-file', '-o', type=click.Path(), 
              help='Output file (default: overwrite input)')
@click.option('--strategy', '-s', type=click.Choice(['complete', 'partial', 'mark']),
              default='complete', help='Cleaning strategy')
@click.option('--threshold', '-t', default=0.7, type=float,
              help='Confidence threshold for AI detection (0.0-1.0)')
@click.option('--backup', '-b', is_flag=True, 
              help='Create backup of original file')
def clean_file(input_file: str, output_file: Optional[str], strategy: str, 
               threshold: float, backup: bool):
    """Clean AI-generated content from a text file."""
    input_path = Path(input_file)
    
    if not input_path.exists():
        click.echo(f"Error: Input file '{input_file}' not found", err=True)
        sys.exit(1)
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        click.echo(f"Error reading file: {e}", err=True)
        sys.exit(1)
    
    # Create backup if requested
    if backup:
        backup_path = input_path.with_suffix(input_path.suffix + '.backup')
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            click.echo(f"Backup created: {backup_path}")
        except Exception as e:
            click.echo(f"Warning: Could not create backup: {e}", err=True)
    
    # Clean the content
    detector = AITextDetector()
    detector.set_confidence_threshold(threshold)
    
    cleaner = TextCleaner(detector)
    result = cleaner.clean_text(content, strategy)
    
    # Determine output file
    output_path = Path(output_file) if output_file else input_path
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result["cleaned_text"])
        
        click.echo(f"File cleaned successfully: {output_path}")
        click.echo(f"Modified: {'Yes' if result['was_modified'] else 'No'}")
        click.echo(f"Confidence: {result['confidence']:.2f}")
        
    except Exception as e:
        click.echo(f"Error writing file: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--pattern', '-p', default='*.txt', 
              help='File pattern to match (default: *.txt)')
@click.option('--strategy', '-s', type=click.Choice(['complete', 'partial', 'mark']),
              default='complete', help='Cleaning strategy')
@click.option('--threshold', '-t', default=0.7, type=float,
              help='Confidence threshold for AI detection (0.0-1.0)')
@click.option('--backup', '-b', is_flag=True,
              help='Create backup of original files')
@click.option('--dry-run', '-n', is_flag=True,
              help='Show what would be done without making changes')
def clean_directory(directory: str, pattern: str, strategy: str, 
                   threshold: float, backup: bool, dry_run: bool):
    """Clean AI-generated content from all files in a directory."""
    dir_path = Path(directory)
    
    if not dir_path.is_dir():
        click.echo(f"Error: '{directory}' is not a directory", err=True)
        sys.exit(1)
    
    # Find matching files
    files = list(dir_path.glob(pattern))
    
    if not files:
        click.echo(f"No files matching pattern '{pattern}' found in '{directory}'")
        return
    
    click.echo(f"Found {len(files)} files matching pattern '{pattern}'")
    
    if dry_run:
        click.echo("DRY RUN - No files will be modified:")
    
    detector = AITextDetector()
    detector.set_confidence_threshold(threshold)
    cleaner = TextCleaner(detector)
    
    total_processed = 0
    total_modified = 0
    
    for file_path in files:
        if dry_run:
            click.echo(f"Would process: {file_path}")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = cleaner.clean_text(content, strategy)
            
            if result["was_modified"]:
                # Create backup if requested
                if backup:
                    backup_path = file_path.with_suffix(file_path.suffix + '.backup')
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                # Write cleaned content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(result["cleaned_text"])
                
                total_modified += 1
                click.echo(f"✓ Cleaned: {file_path} (confidence: {result['confidence']:.2f})")
            else:
                click.echo(f"- Skipped: {file_path} (no AI content detected)")
            
            total_processed += 1
            
        except Exception as e:
            click.echo(f"✗ Error processing {file_path}: {e}", err=True)
    
    if not dry_run:
        click.echo(f"\nProcessed {total_processed} files, modified {total_modified}")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
#!/usr/bin/env python
"""
PodcastGenerator Environment Demo

This script demonstrates how to use the PodcastGenerator with environment variables
loaded from a .env file.
"""

import os
import sys
from podcast_generator.config import get_config
from podcast_generator.main import PodcastGenerator

def main():
    """Demonstrate using PodcastGenerator with .env configuration."""
    # Check if we have a .env file
    if not os.path.exists('.env'):
        print("Error: No .env file found in the current directory.")
        print("Please copy .env.example to .env and fill in your API keys.")
        return 1
    
    # Load configuration from .env file
    cfg = get_config()
    
    # Check if OpenAI API key is available
    if not cfg.openai_api_key:
        print("Warning: No OpenAI API key found in .env file or environment.")
        print("Script generation step will fail without a valid API key.")
        print("Please add OPENAI_API_KEY to your .env file.")
        return 1
    
    # Print configuration (with API keys partially redacted for security)
    print("Loaded configuration:")
    redacted_config = cfg.as_dict()
    
    # Redact sensitive information
    if redacted_config["openai_api_key"]:
        key = redacted_config["openai_api_key"]
        redacted_config["openai_api_key"] = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "****"
    
    if redacted_config["aws_access_key"]:
        key = redacted_config["aws_access_key"]
        redacted_config["aws_access_key"] = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "****"
    
    if redacted_config["aws_secret_key"]:
        redacted_config["aws_secret_key"] = "********" 
    
    for key, value in redacted_config.items():
        print(f"  {key}: {value}")
    
    # Load sample article
    sample_file = "sample_article.txt"
    if not os.path.exists(sample_file):
        print(f"Error: Sample article file '{sample_file}' not found.")
        return 1
    
    with open(sample_file, "r", encoding="utf-8") as f:
        # Just use the abstract for a quick demo
        article_text = f.read().split("## Introduction")[0]
    
    print("\nInitializing PodcastGenerator with configuration from .env file...")
    
    # Initialize the generator - it will automatically use values from .env
    generator = PodcastGenerator()
    
    # Set up output paths
    output_dir = "env_demo_output"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "env_demo_podcast.mp3")
    
    # Generate podcast
    print(f"\nGenerating podcast to {output_file}...")
    report = generator.generate(
        article_text=article_text,
        output_file=output_file,
        save_script=True
    )
    
    print("\nDemo completed successfully!")
    print(f"Summary length: {report['summary_length']} characters")
    print(f"Script length: {report['script_length']} characters")
    print(f"Verification percentage: {report['verification_percentage']:.2f}%")
    print(f"Output file: {report['output_file']}")
    print(f"Script file: {os.path.splitext(output_file)[0]}_script.txt")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
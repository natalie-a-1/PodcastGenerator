#!/usr/bin/env python
"""
PodcastGenerator Demo

This script demonstrates how to use the PodcastGenerator to create a podcast
from a research article.
"""

import os
import argparse
from podcast_generator.main import PodcastGenerator

def main():
    """Demo the PodcastGenerator functionality."""
    parser = argparse.ArgumentParser(description="Demo the PodcastGenerator.")
    parser.add_argument("--openai-api-key", help="OpenAI API key for GPT-4.")
    parser.add_argument("--use-polly", action="store_true", help="Use AWS Polly for TTS.")
    parser.add_argument("--aws-access-key", help="AWS access key for Polly.")
    parser.add_argument("--aws-secret-key", help="AWS secret key for Polly.")
    parser.add_argument("--input-file", default="sample_article.txt", help="Input article file.")
    parser.add_argument("--output-file", default="demo_podcast.mp3", help="Output podcast file.")
    
    args = parser.parse_args()
    
    # Check if OpenAI API key is provided or in environment
    openai_api_key = args.openai_api_key or os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        print("Warning: No OpenAI API key provided. Script generation may fail.")
        print("Please provide an API key with --openai-api-key or set the OPENAI_API_KEY environment variable.")
    
    # Initialize the PodcastGenerator
    generator = PodcastGenerator(
        openai_api_key=openai_api_key,
        use_polly=args.use_polly,
        aws_access_key=args.aws_access_key,
        aws_secret_key=args.aws_secret_key
    )
    
    # Read the article text
    try:
        print(f"Reading article from {args.input_file}...")
        with open(args.input_file, "r", encoding="utf-8") as f:
            article_text = f.read()
            
        # For demo purposes, let's limit to the abstract and introduction
        if len(article_text) > 10000:
            parts = article_text.split("## Methodology")
            if len(parts) > 1:
                article_text = parts[0]
                print("Using only the abstract and introduction for this demo.")
    except Exception as e:
        print(f"Error reading input file: {e}")
        return 1
    
    # Generate the podcast
    try:
        print(f"\nGenerating podcast '{args.output_file}'...")
        report = generator.generate(
            article_text=article_text,
            output_file=args.output_file,
            save_script=True,
            script_file=f"{os.path.splitext(args.output_file)[0]}_script.txt"
        )
        
        # Print the generation report
        print("\nGeneration Report:")
        print(f"Summary length: {report['summary_length']} characters")
        print(f"Script length: {report['script_length']} characters")
        print(f"Verification percentage: {report['verification_percentage']:.2f}%")
        print(f"Output file: {report['output_file']}")
        
        print("\nDemo completed successfully! 🎉")
        print(f"Podcast saved to: {args.output_file}")
        print(f"Script saved to: {os.path.splitext(args.output_file)[0]}_script.txt")
        
        return 0
    except Exception as e:
        print(f"Error generating podcast: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 
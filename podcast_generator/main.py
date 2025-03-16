"""
PodcastGenerator - Main module.

This is the main module that coordinates the workflow between the different
components of the podcast generator.
"""

import os
import argparse
import json
from .analyzer import ResearchAnalyzer
from .composer import ScriptComposer
from .fact_checker import FactChecker
from .audio_producer import AudioProducer
from .config import config, get_config


class PodcastGenerator:
    """Main class for generating podcasts from research articles."""
    
    def __init__(self, openai_api_key=None, use_polly=None, aws_access_key=None, aws_secret_key=None, env_file=None):
        """Initialize the podcast generator with the required components.
        
        Args:
            openai_api_key (str, optional): OpenAI API key for GPT-4. If None, uses from config.
            use_polly (bool, optional): Whether to use AWS Polly for text-to-speech. If None, uses from config.
            aws_access_key (str, optional): AWS access key for Polly. If None, uses from config.
            aws_secret_key (str, optional): AWS secret key for Polly. If None, uses from config.
            env_file (str, optional): Path to a .env file to load configuration from.
        """
        print("Initializing PodcastGenerator...")
        
        # Load configuration from environment or .env file
        self.cfg = get_config(env_file) if env_file else config
        
        # Override config with explicit parameters if provided
        openai_api_key = openai_api_key or self.cfg.openai_api_key
        use_polly = use_polly if use_polly is not None else self.cfg.use_polly
        aws_access_key = aws_access_key or self.cfg.aws_access_key
        aws_secret_key = aws_secret_key or self.cfg.aws_secret_key
        
        # Initialize the components
        self.analyzer = ResearchAnalyzer(model_name=self.cfg.summarization_model)
        self.composer = ScriptComposer(api_key=openai_api_key)
        self.fact_checker = FactChecker(model_name=self.cfg.fact_check_model)
        self.audio_producer = AudioProducer(
            use_polly=use_polly, 
            aws_access_key=aws_access_key, 
            aws_secret_key=aws_secret_key,
            region=self.cfg.aws_region
        )
        
        print("PodcastGenerator initialized successfully.")
    
    def generate(self, article_text, output_file=None, save_script=None, script_file=None):
        """Generate a podcast from the given article text.
        
        Args:
            article_text (str): The text of the research article.
            output_file (str, optional): The path to the output audio file. If None, uses a default path.
            save_script (bool, optional): Whether to save the generated script to a file. If None, uses config value.
            script_file (str, optional): The path to save the script if save_script is True.
                                        If None, will use the output file name with .txt extension.
            
        Returns:
            dict: Generation report containing information about the process.
        """
        # Use defaults from config if not explicitly provided
        if output_file is None:
            os.makedirs(self.cfg.default_output_dir, exist_ok=True)
            output_file = os.path.join(self.cfg.default_output_dir, "podcast.mp3")
        
        if save_script is None:
            save_script = self.cfg.save_scripts
        
        print("\n================ Starting Podcast Generation ================\n")
        
        # Step 1: Analyze and summarize the article
        print("\n--- Step 1: Research Analysis ---\n")
        summary = self.analyzer.summarize(article_text)
        
        # Step 2: Generate the script
        print("\n--- Step 2: Script Composition ---\n")
        script = self.composer.generate_script(summary)
        
        # Step 3: Verify the script
        print("\n--- Step 3: Fact Checking ---\n")
        is_verified, verification_report = self.fact_checker.verify_script(script, article_text)
        
        # If the script is not verified, filter out unverified statements
        if not is_verified:
            print(f"Script verification score: {verification_report['verification_percentage']:.2f}%")
            print("Filtering out unverified statements...")
            script = self.fact_checker.filter_script(script, article_text)
        
        # Step 4: Produce the podcast
        print("\n--- Step 4: Audio Production ---\n")
        podcast_file = self.audio_producer.produce_podcast(script, output_file)
        
        # Save the script if requested
        if save_script:
            if script_file is None:
                base_name = os.path.splitext(output_file)[0]
                script_file = f"{base_name}_script.txt"
            
            with open(script_file, "w", encoding="utf-8") as f:
                f.write(script)
            
            print(f"Script saved to {script_file}")
        
        # Create a report
        report = {
            "summary_length": len(summary),
            "script_length": len(script),
            "verification_percentage": verification_report["verification_percentage"],
            "output_file": podcast_file
        }
        
        print("\n================ Podcast Generation Complete ================\n")
        print(f"Podcast saved to: {podcast_file}")
        
        return report


def main():
    """Command-line interface for the podcast generator."""
    parser = argparse.ArgumentParser(description="Generate a podcast from a research article.")
    parser.add_argument("input_file", help="Path to the research article text file.")
    parser.add_argument("--output", "-o", default=None, help="Output podcast file path.")
    parser.add_argument("--save-script", "-s", action="store_true", dest="save_script", 
                        default=None, help="Save the generated script.")
    parser.add_argument("--no-save-script", action="store_false", dest="save_script",
                       help="Don't save the generated script.")
    parser.add_argument("--script-file", help="Path to save the script (if saving script).")
    parser.add_argument("--openai-api-key", help="OpenAI API key for GPT-4.")
    parser.add_argument("--use-polly", action="store_true", help="Use AWS Polly for text-to-speech.")
    parser.add_argument("--aws-access-key", help="AWS access key for Polly.")
    parser.add_argument("--aws-secret-key", help="AWS secret key for Polly.")
    parser.add_argument("--report", "-r", help="Path to save the generation report (JSON).")
    parser.add_argument("--env-file", help="Path to a .env file to load configuration from.")
    
    args = parser.parse_args()
    
    # Read the input file
    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            article_text = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}")
        return 1
    
    # Create the podcast generator
    generator = PodcastGenerator(
        openai_api_key=args.openai_api_key,
        use_polly=args.use_polly if args.use_polly is not None else None,
        aws_access_key=args.aws_access_key,
        aws_secret_key=args.aws_secret_key,
        env_file=args.env_file
    )
    
    # Generate the podcast
    try:
        report = generator.generate(
            article_text,
            output_file=args.output,
            save_script=args.save_script,
            script_file=args.script_file
        )
        
        # Save the report if requested
        if args.report:
            os.makedirs(os.path.dirname(os.path.abspath(args.report)), exist_ok=True)
            with open(args.report, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            print(f"Report saved to {args.report}")
        
        return 0
    except Exception as e:
        print(f"Error generating podcast: {e}")
        return 1


if __name__ == "__main__":
    exit(main()) 
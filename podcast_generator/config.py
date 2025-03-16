"""
Configuration module for PodcastGenerator.

This module handles loading environment variables and configuration settings
from the .env file or environment.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Try to import dotenv, but don't fail if it's not installed
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# Set up logging
logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for PodcastGenerator."""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration from environment or .env file.
        
        Args:
            env_file (str, optional): Path to the .env file. If None, tries to find
                                     .env in the current directory or parent directories.
        """
        self._load_environment(env_file)
        self._initialize_config()
    
    def _load_environment(self, env_file: Optional[str]) -> None:
        """Load environment variables from .env file if available.
        
        Args:
            env_file (str, optional): Path to the .env file.
        """
        # If dotenv is available, try to load from .env file
        if DOTENV_AVAILABLE:
            if env_file and Path(env_file).exists():
                load_dotenv(env_file)
                logger.info(f"Loaded environment from {env_file}")
            else:
                # Try to find .env in current or parent directories
                for path in [".env", "../.env", "../../.env"]:
                    if Path(path).exists():
                        load_dotenv(path)
                        logger.info(f"Loaded environment from {path}")
                        break
        
    def _initialize_config(self) -> None:
        """Initialize configuration from environment variables."""
        # OpenAI credentials
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        
        # AWS credentials
        self.use_polly = os.environ.get("USE_POLLY", "false").lower() == "true"
        self.aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.environ.get("AWS_REGION", "us-east-1")
        
        # Model configuration
        self.summarization_model = os.environ.get("SUMMARIZATION_MODEL", "facebook/bart-large-cnn")
        self.fact_check_model = os.environ.get("FACT_CHECK_MODEL", 
                                             "sentence-transformers/roberta-large-nli-stsb-mean-tokens")
        
        # Output configuration
        self.default_output_dir = os.environ.get("DEFAULT_OUTPUT_DIR", "./outputs")
        self.save_scripts = os.environ.get("SAVE_SCRIPTS", "true").lower() == "true"
        
        # Runtime configuration
        self.debug = os.environ.get("DEBUG", "false").lower() == "true"
    
    def as_dict(self) -> Dict[str, Any]:
        """Return the configuration as a dictionary.
        
        Returns:
            dict: Dictionary containing all configuration values.
        """
        return {
            "openai_api_key": self.openai_api_key,
            "use_polly": self.use_polly,
            "aws_access_key": self.aws_access_key,
            "aws_secret_key": self.aws_secret_key,
            "aws_region": self.aws_region,
            "summarization_model": self.summarization_model,
            "fact_check_model": self.fact_check_model,
            "default_output_dir": self.default_output_dir,
            "save_scripts": self.save_scripts,
            "debug": self.debug
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key.
        
        Args:
            key (str): The configuration key.
            default: The default value if the key doesn't exist.
            
        Returns:
            The configuration value.
        """
        return self.as_dict().get(key, default)


# Create a default configuration
config = Config()

# For easy importing
def get_config(env_file: Optional[str] = None) -> Config:
    """Get a configuration instance.
    
    Args:
        env_file (str, optional): Path to the .env file.
        
    Returns:
        Config: A configuration instance.
    """
    if env_file:
        return Config(env_file)
    return config 
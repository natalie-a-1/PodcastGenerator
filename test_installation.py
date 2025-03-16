#!/usr/bin/env python
"""
Test script to verify that all required dependencies are installed correctly.
"""

import sys
import importlib.util

def check_package(package_name):
    """Check if a package is installed and importable."""
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(f"❌ {package_name} is NOT installed")
        return False
    else:
        print(f"✅ {package_name} is installed")
        return True

def main():
    """Main function to check all required packages."""
    print("Testing PodcastGenerator installation...\n")
    
    required_packages = [
        # Core modules
        "podcast_generator",
        "transformers",
        "torch",
        "openai",
        "sentence_transformers",
        "gtts",
        "boto3",
        "pydub",
        "numpy",
        "tqdm"
    ]
    
    all_installed = True
    for package in required_packages:
        if not check_package(package):
            all_installed = False
    
    if all_installed:
        print("\nAll required packages are installed! 🎉")
        print("PodcastGenerator should be ready to use.")
    else:
        print("\nSome packages are missing. Please install them with:")
        print("pip install -r requirements.txt")
    
    return 0 if all_installed else 1

if __name__ == "__main__":
    sys.exit(main()) 
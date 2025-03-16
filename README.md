# PodcastGenerator

A lightweight Python module that generates a 5-minute podcast audio file from research article text.

## Overview

PodcastGenerator transforms research articles into engaging, podcast-style audio content through four components:

1. **Research Analyzer**: Summarizes the article using facebook/bart-large-cnn.
2. **Script Composer**: Generates dialogue script for two hosts (Alex and Sam) using GPT-4.
3. **Fact-Checker**: Verifies script content against the original article using sentence-transformers.
4. **Audio Producer**: Converts the script into a 5-minute MP3 file with two distinct voices.

## Installation

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

### Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/PodcastGenerator.git
cd PodcastGenerator
```

2. Set up a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. (Optional) Install the package in development mode
```bash
pip install -e .
```

5. Configure API keys
```bash
# Copy the example .env file
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use any text editor
```

## Usage

### Command Line Interface

Generate a podcast from a research article text file:

```bash
python generate_podcast.py sample_article.txt --output my_podcast.mp3 --save-script
```

#### Options

- `input_file`: Path to the research article text file (required)
- `--output`, `-o`: Output podcast file path (default: podcast.mp3)
- `--save-script`, `-s`: Save the generated script to a file
- `--script-file`: Path to save the script (if --save-script is used)
- `--openai-api-key`: OpenAI API key for GPT-4
- `--use-polly`: Use AWS Polly for text-to-speech (requires AWS credentials)
- `--aws-access-key`: AWS access key for Polly
- `--aws-secret-key`: AWS secret key for Polly
- `--report`, `-r`: Path to save the generation report (JSON)
- `--env-file`: Path to a specific .env file (optional)

### Python API

You can also use PodcastGenerator as a Python module in your code:

```python
from podcast_generator.main import PodcastGenerator

# Initialize the generator
generator = PodcastGenerator(
    openai_api_key="your-openai-api-key",  # Optional
    use_polly=False,  # Use AWS Polly instead of gTTS
    aws_access_key="your-aws-access-key",  # Optional
    aws_secret_key="your-aws-secret-key"   # Optional
)

# Read the article text
with open("sample_article.txt", "r", encoding="utf-8") as f:
    article_text = f.read()

# Generate the podcast
report = generator.generate(
    article_text=article_text,
    output_file="my_podcast.mp3",
    save_script=True,
    script_file="my_podcast_script.txt"  # Optional
)

# Print the generation report
print(f"Summary length: {report['summary_length']}")
print(f"Script length: {report['script_length']}")
print(f"Verification percentage: {report['verification_percentage']:.2f}%")
print(f"Output file: {report['output_file']}")
```

## API Keys and Credentials

### Using Environment Variables

The recommended way to provide API keys is through environment variables or a `.env` file:

1. Copy the example file: `cp .env.example .env`
2. Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=sk-your-openai-api-key
   USE_POLLY=false
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   ```
3. The application will automatically load credentials from the `.env` file

### OpenAI API Key

For script generation using GPT-4, you need an OpenAI API key. You can provide it in several ways:

1. In your `.env` file: `OPENAI_API_KEY=sk-your-key`
2. Pass it directly to the constructor: `PodcastGenerator(openai_api_key="your-key")`
3. Set it as an environment variable: `export OPENAI_API_KEY="your-key"`
4. Provide it via the command line: `--openai-api-key "your-key"`

### AWS Credentials (for Polly)

To use AWS Polly for more natural-sounding voices:

1. In your `.env` file:
   ```
   USE_POLLY=true
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_REGION=us-east-1
   ```
2. Pass credentials to the constructor: `PodcastGenerator(use_polly=True, aws_access_key="...", aws_secret_key="...")`
3. Set environment variables: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
4. Provide them via the command line: `--use-polly --aws-access-key "..." --aws-secret-key "..."`

## Customization

### Configuration Options in .env

You can customize various settings in your `.env` file:

```
# Model Configuration
SUMMARIZATION_MODEL=facebook/bart-large-cnn
FACT_CHECK_MODEL=sentence-transformers/roberta-large-nli-stsb-mean-tokens

# Output Configuration
DEFAULT_OUTPUT_DIR=./outputs
SAVE_SCRIPTS=true

# Runtime Configuration
DEBUG=false
```

### Voice Selection

By default, the podcast uses two voices:
- For gTTS: A single voice is used with speaker labels
- For AWS Polly: "Matthew" for Alex and "Joanna" for Sam

You can customize this by modifying the `host_voices` parameter in the `produce_podcast` method.

### Duration

The default duration is 5 minutes. The system generates an appropriate amount of content and adjusts the speed if necessary to fit the target duration.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- BART model for summarization: facebook/bart-large-cnn
- Sentence transformers for fact-checking: sentence-transformers/roberta-large-nli-stsb-mean-tokens
- Text-to-speech: gTTS and AWS Polly 
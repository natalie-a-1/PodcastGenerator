"""
Research Analyzer - Summarizes research articles.

This module uses the facebook/bart-large-cnn model to generate concise
summaries of research articles for podcast script generation.
"""

import torch
from transformers import BartTokenizer, BartForConditionalGeneration
from tqdm import tqdm

class ResearchAnalyzer:
    """Class for summarizing research articles using BART."""
    
    def __init__(self, model_name="facebook/bart-large-cnn"):
        """Initialize the analyzer with the specified model.
        
        Args:
            model_name (str): The name of the model to use for summarization.
        """
        print(f"Loading summarization model: {model_name}")
        self.tokenizer = BartTokenizer.from_pretrained(model_name)
        self.model = BartForConditionalGeneration.from_pretrained(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        print(f"Model loaded successfully on {self.device}")
    
    def summarize(self, text, max_length=1024, min_length=150):
        """Summarize the input text.
        
        Args:
            text (str): The research article text to summarize.
            max_length (int): Maximum length of the generated summary.
            min_length (int): Minimum length of the generated summary.
            
        Returns:
            str: The generated summary.
        """
        print("Analyzing research article...")
        # Split text into chunks if it's too long for the model
        max_token_length = 1024  # BART model's maximum input length
        
        # Tokenize without adding special tokens to get accurate token count
        tokens = self.tokenizer(text, add_special_tokens=False, truncation=False)["input_ids"]
        
        # Process in chunks if necessary
        summaries = []
        
        # If text fits in one chunk
        if len(tokens) <= max_token_length:
            inputs = self.tokenizer(text, return_tensors="pt", max_length=max_token_length, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                summary_ids = self.model.generate(
                    inputs["input_ids"], 
                    attention_mask=inputs["attention_mask"],
                    max_length=max_length,
                    min_length=min_length,
                    num_beams=4,
                    length_penalty=2.0,
                    early_stopping=True
                )
            
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            summaries.append(summary)
        else:
            # Process text in chunks of max_token_length
            text_chunks = []
            chunk = []
            chunk_length = 0
            
            for token in tokens:
                if chunk_length + 1 <= max_token_length - 2:  # Account for special tokens
                    chunk.append(token)
                    chunk_length += 1
                else:
                    text_chunks.append(self.tokenizer.decode(chunk))
                    chunk = [token]
                    chunk_length = 1
            
            if chunk:  # Add the last chunk if it's not empty
                text_chunks.append(self.tokenizer.decode(chunk))
            
            # Process each chunk
            for i, chunk in enumerate(tqdm(text_chunks, desc="Summarizing chunks")):
                inputs = self.tokenizer(chunk, return_tensors="pt", max_length=max_token_length, truncation=True)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    chunk_length = min(max_length // len(text_chunks), max_length // 2)
                    chunk_min_length = min(min_length // len(text_chunks), min_length // 2)
                    
                    summary_ids = self.model.generate(
                        inputs["input_ids"],
                        attention_mask=inputs["attention_mask"],
                        max_length=chunk_length,
                        min_length=chunk_min_length,
                        num_beams=4,
                        length_penalty=2.0,
                        early_stopping=True
                    )
                
                summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                summaries.append(summary)
        
        # Combine all summaries
        full_summary = " ".join(summaries)
        
        # If the combined summary is still too long, summarize it again
        if len(self.tokenizer(full_summary)["input_ids"]) > max_length:
            print("Refining summary to ensure optimal length...")
            inputs = self.tokenizer(full_summary, return_tensors="pt", max_length=max_token_length, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                summary_ids = self.model.generate(
                    inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_length=max_length,
                    min_length=min_length,
                    num_beams=4, 
                    length_penalty=2.0,
                    early_stopping=True
                )
            
            full_summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        print("Research analysis complete.")
        return full_summary 
"""
Fact Checker - Verifies script content against the original article.

This module ensures that the generated podcast script only contains information
that is directly supported by the original research article.
"""

import re
from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np
from tqdm import tqdm

class FactChecker:
    """Class for checking script facts against the original article."""
    
    def __init__(self, model_name="sentence-transformers/roberta-large-nli-stsb-mean-tokens"):
        """Initialize the fact checker with the specified model.
        
        Args:
            model_name (str): The name of the model to use for semantic similarity.
        """
        print(f"Loading fact-checking model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        print(f"Fact checking model loaded successfully on {self.device}")
    
    def _extract_statements(self, script):
        """Extract factual statements from the script.
        
        Args:
            script (str): The podcast script.
            
        Returns:
            list: List of factual statements from the script.
        """
        # Split script into lines by host
        lines = script.strip().split('\n')
        statements = []
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
                
            # Try to separate speaker from content
            match = re.match(r'^([^:]+):\s*(.+)$', line)
            if match:
                speaker, content = match.groups()
                # Split content into sentences using regex
                sentences = re.split(r'(?<=[.!?])\s+', content)
                statements.extend([s.strip() for s in sentences if s.strip()])
        
        return statements
    
    def _extract_source_sentences(self, article):
        """Extract sentences from the source article.
        
        Args:
            article (str): The original research article.
            
        Returns:
            list: List of sentences from the article.
        """
        # Split article into sentences
        sentences = re.split(r'(?<=[.!?])\s+', article)
        return [s.strip() for s in sentences if s.strip()]
    
    def verify_script(self, script, article, similarity_threshold=0.7):
        """Verify that the script is factually consistent with the article.
        
        Args:
            script (str): The podcast script to check.
            article (str): The original research article.
            similarity_threshold (float): Minimum semantic similarity score to consider a statement supported.
            
        Returns:
            tuple: (is_verified, report) where:
                - is_verified (bool): True if all statements are verified, False otherwise.
                - report (dict): Detailed verification report.
        """
        print("Verifying script against original article...")
        
        # Extract statements and sentences
        statements = self._extract_statements(script)
        sentences = self._extract_source_sentences(article)
        
        print(f"Extracted {len(statements)} statements from script and {len(sentences)} sentences from article.")
        
        # Encode statements and sentences
        statement_embeddings = self.model.encode(statements, show_progress_bar=True)
        sentence_embeddings = self.model.encode(sentences, show_progress_bar=True)
        
        # Check each statement against all sentences
        verification_results = []
        verified_count = 0
        
        for i, statement in enumerate(tqdm(statements, desc="Verifying statements")):
            # Calculate cosine similarity between this statement and all sentences
            similarities = util.pytorch_cos_sim(
                statement_embeddings[i].reshape(1, -1), 
                sentence_embeddings
            )[0]
            
            # Get the best match
            best_match_idx = torch.argmax(similarities).item()
            best_match_score = similarities[best_match_idx].item()
            best_match_text = sentences[best_match_idx]
            
            # Check if the statement is verified
            is_verified = best_match_score >= similarity_threshold
            
            if is_verified:
                verified_count += 1
                
            verification_results.append({
                "statement": statement,
                "best_match": best_match_text,
                "similarity_score": best_match_score,
                "is_verified": is_verified
            })
        
        # Calculate verification percentage
        verification_percentage = (verified_count / len(statements)) * 100 if statements else 100
        
        # Create verification report
        report = {
            "total_statements": len(statements),
            "verified_statements": verified_count,
            "verification_percentage": verification_percentage,
            "details": verification_results
        }
        
        is_verified = verification_percentage >= 90  # Consider verified if at least 90% statements are verified
        
        print(f"Verification complete: {verified_count}/{len(statements)} statements verified ({verification_percentage:.2f}%).")
        
        return is_verified, report
    
    def filter_script(self, script, article, similarity_threshold=0.7):
        """Filter out unverified statements from the script.
        
        Args:
            script (str): The podcast script to filter.
            article (str): The original research article.
            similarity_threshold (float): Minimum semantic similarity score to keep a statement.
            
        Returns:
            str: The filtered script with unverified facts removed.
        """
        print("Filtering script to remove unverified statements...")
        
        # First, verify the script
        _, report = self.verify_script(script, article, similarity_threshold)
        
        # If all statements are verified, return the original script
        if report["verification_percentage"] == 100:
            print("All statements verified. No filtering needed.")
            return script
            
        # Extract statements and their verification status
        verified_map = {item["statement"]: item["is_verified"] for item in report["details"]}
        
        # Split script into lines
        lines = script.strip().split('\n')
        filtered_lines = []
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                filtered_lines.append(line)
                continue
                
            # Try to separate speaker from content
            match = re.match(r'^([^:]+):\s*(.+)$', line)
            if match:
                speaker, content = match.groups()
                
                # Split content into sentences
                sentences = re.split(r'(?<=[.!?])\s+', content)
                verified_sentences = []
                
                for sentence in sentences:
                    sentence_stripped = sentence.strip()
                    # If sentence is in verified_map and is verified, keep it
                    if sentence_stripped in verified_map and verified_map[sentence_stripped]:
                        verified_sentences.append(sentence)
                
                # If there are verified sentences, add them back to the script
                if verified_sentences:
                    filtered_line = f"{speaker}: {' '.join(verified_sentences)}"
                    filtered_lines.append(filtered_line)
            else:
                # Keep lines that don't match the speaker pattern (e.g., stage directions)
                filtered_lines.append(line)
        
        filtered_script = '\n'.join(filtered_lines)
        print("Script filtering complete.")
        
        return filtered_script 
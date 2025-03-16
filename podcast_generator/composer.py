"""
Script Composer - Generates podcast scripts from article summaries.

This module uses GPT-4 to create engaging dialogue scripts for podcast hosts
based on summarized research articles.
"""

import openai
import time
import json

class ScriptComposer:
    """Class for generating podcast scripts using GPT-4."""
    
    def __init__(self, api_key=None):
        """Initialize the script composer with the specified API key.
        
        Args:
            api_key (str, optional): OpenAI API key. If None, must be set in the environment.
        """
        if api_key:
            openai.api_key = api_key
        print("Script composer initialized.")
    
    def generate_script(self, summary, duration_minutes=5, hosts=("Alex", "Sam")):
        """Generate a podcast script from the given summary.
        
        Args:
            summary (str): The summary of the research article.
            duration_minutes (int): The target duration of the podcast in minutes.
            hosts (tuple): Names of the podcast hosts.
            
        Returns:
            str: The generated script in a dialogue format.
        """
        print("Generating podcast script...")
        
        # Calculate approximate word count for target duration
        # Average speaking pace is ~150 words per minute
        target_word_count = duration_minutes * 150
        
        # Prompt engineering for GPT-4
        system_prompt = f"""
        You are an expert podcast script writer. Create an engaging, conversational script for a 
        {duration_minutes}-minute podcast episode featuring two hosts named {hosts[0]} and {hosts[1]}.
        
        The script should:
        1. Be based STRICTLY on the research summary provided, with NO additional information
        2. Have a natural, engaging dialogue flow between the hosts
        3. Include an introduction, body discussing key points, and conclusion
        4. Be approximately {target_word_count} words total to fit the {duration_minutes}-minute format
        5. Format the script as a dialogue with speaker names followed by their lines

        Format example:
        {hosts[0]}: Welcome to today's episode where we'll be discussing...
        {hosts[1]}: That's right, and this research is particularly interesting because...
        
        DO NOT add any content that is not directly supported by the summary!
        """
        
        tries = 0
        max_tries = 3
        delay = 5  # seconds
        
        while tries < max_tries:
            try:
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Research Summary:\n\n{summary}"}
                    ],
                    temperature=0.7,
                    max_tokens=4000
                )
                
                script = response.choices[0].message.content.strip()
                print("Script generation complete.")
                return script
                
            except Exception as e:
                tries += 1
                print(f"Error generating script (attempt {tries}/{max_tries}): {e}")
                if tries < max_tries:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    raise Exception(f"Failed to generate script after {max_tries} attempts: {e}") 
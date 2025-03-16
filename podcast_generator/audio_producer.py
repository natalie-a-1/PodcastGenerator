"""
Audio Producer - Converts scripts to audio podcast files.

This module takes a podcast script and generates an audio file with
different voices for different speakers.
"""

import os
import re
import time
import tempfile
from gtts import gTTS
from pydub import AudioSegment
from tqdm import tqdm
import boto3

class AudioProducer:
    """Class for converting scripts to audio files."""
    
    def __init__(self, use_polly=False, aws_access_key=None, aws_secret_key=None, region="us-east-1"):
        """Initialize the audio producer.
        
        Args:
            use_polly (bool): Whether to use AWS Polly for TTS (if False, use gTTS).
            aws_access_key (str, optional): AWS access key for Polly.
            aws_secret_key (str, optional): AWS secret key for Polly.
            region (str): AWS region for Polly.
        """
        self.use_polly = use_polly
        
        if use_polly:
            # Initialize AWS Polly client
            session = boto3.Session(
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region
            )
            self.polly_client = session.client('polly')
            print("AWS Polly initialized for text-to-speech.")
        else:
            print("Google TTS initialized for text-to-speech.")
    
    def _text_to_speech_gtts(self, text, output_path, lang='en', slow=False):
        """Convert text to speech using Google TTS.
        
        Args:
            text (str): The text to convert.
            output_path (str): The path to save the audio file.
            lang (str): The language of the text.
            slow (bool): Whether to speak slowly.
            
        Returns:
            str: The path to the generated audio file.
        """
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(output_path)
        return output_path
    
    def _text_to_speech_polly(self, text, output_path, voice_id='Matthew', text_type='text'):
        """Convert text to speech using AWS Polly.
        
        Args:
            text (str): The text to convert.
            output_path (str): The path to save the audio file.
            voice_id (str): The voice ID to use.
            text_type (str): The type of input text ('text' or 'ssml').
            
        Returns:
            str: The path to the generated audio file.
        """
        try:
            response = self.polly_client.synthesize_speech(
                Engine='neural',
                OutputFormat='mp3',
                Text=text,
                TextType=text_type,
                VoiceId=voice_id
            )
            
            # Save the audio stream to file
            with open(output_path, 'wb') as file:
                file.write(response['AudioStream'].read())
            
            return output_path
        except Exception as e:
            print(f"Error using Polly: {e}")
            print("Falling back to gTTS...")
            return self._text_to_speech_gtts(text, output_path)
    
    def _parse_script(self, script):
        """Parse the script into speaker segments.
        
        Args:
            script (str): The podcast script.
            
        Returns:
            list: List of (speaker, text) tuples.
        """
        lines = script.strip().split('\n')
        segments = []
        
        for line in lines:
            if not line.strip():
                continue
                
            # Try to separate speaker from content
            match = re.match(r'^([^:]+):\s*(.+)$', line)
            if match:
                speaker, content = match.groups()
                segments.append((speaker.strip(), content.strip()))
        
        return segments
    
    def produce_podcast(self, script, output_file="podcast.mp3", host_voices=None):
        """Produce a podcast from the given script.
        
        Args:
            script (str): The podcast script.
            output_file (str): The path to the output audio file.
            host_voices (dict, optional): Mapping of host names to voice IDs (for Polly).
                                         If None, defaults will be used.
            
        Returns:
            str: The path to the generated audio file.
        """
        print("Producing podcast audio...")
        
        # Parse the script into segments
        segments = self._parse_script(script)
        
        if not segments:
            raise ValueError("Script could not be parsed. Ensure it's in the format 'Speaker: Text'.")
        
        # Set default host voices
        if host_voices is None:
            if self.use_polly:
                host_voices = {
                    "Alex": "Matthew",
                    "Sam": "Joanna"
                }
            else:
                # gTTS doesn't support different voices, so we'll use the same voice for all hosts
                host_voices = {}
        
        # Create a temporary directory for audio segments
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_segments = []
            
            # Generate audio for each segment
            for i, (speaker, text) in enumerate(tqdm(segments, desc="Generating audio segments")):
                segment_path = os.path.join(temp_dir, f"segment_{i}.mp3")
                
                if self.use_polly:
                    # Get voice ID for speaker, or use default
                    voice_id = host_voices.get(speaker, "Matthew")
                    self._text_to_speech_polly(text, segment_path, voice_id=voice_id)
                else:
                    self._text_to_speech_gtts(text, segment_path)
                
                # Load the audio segment
                audio = AudioSegment.from_mp3(segment_path)
                
                # Add a short pause between segments
                if audio_segments:
                    pause = AudioSegment.silent(duration=500)  # 500ms pause
                    audio_segments.append(pause)
                
                audio_segments.append(audio)
                
                # Avoid rate limiting
                time.sleep(0.1)
            
            # Combine all segments into one
            print("Combining audio segments...")
            combined = sum(audio_segments[1:], audio_segments[0]) if audio_segments else AudioSegment.empty()
            
            # Ensure the podcast is the right length (approximately 5 minutes)
            target_duration = 5 * 60 * 1000  # 5 minutes in milliseconds
            current_duration = len(combined)
            
            if current_duration > target_duration * 1.1:  # More than 10% too long
                print(f"Podcast is too long ({current_duration/1000/60:.2f} min). Speeding up to reach target duration...")
                speed_factor = current_duration / target_duration
                combined = combined.speedup(playback_speed=speed_factor)
            
            # Export the final podcast
            print(f"Exporting podcast to {output_file}...")
            combined.export(output_file, format="mp3")
            
            print(f"Podcast production complete. Duration: {len(combined)/1000/60:.2f} minutes")
            
            return output_file 
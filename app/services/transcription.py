"""Transcription Service - Groq Whisper Integration (FREE)"""
import os
from groq import Groq

# Demo transcript for testing without API key
DEMO_TRANSCRIPT = """
Alright team, let's wrap up this meeting. 

John, you'll take care of the user authentication module. Can you have that done by next Friday?

Sure, I can have the auth module ready by Friday the 15th.

Great. Sarah, I need you to review the database schema and propose any optimizations. Let's aim for Wednesday.

Will do. I'll also coordinate with the DevOps team about the staging environment.

Perfect. We've decided to use PostgreSQL instead of MySQL for the new project - it better fits our scaling needs.

One more thing - everyone should update their development environment to Node 20 before our next sprint.

I'll send out the setup instructions by tomorrow.

Thanks everyone. Meeting adjourned.
"""

def get_groq_client():
    """Get Groq client for free Whisper transcription."""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        return None  # Return None for demo mode
    return Groq(api_key=api_key)


def transcribe_audio(filepath: str) -> str:
    """
    Transcribe audio file using Groq's FREE Whisper API.
    Falls back to demo mode if no API key.
    
    Args:
        filepath: Path to the audio file
        
    Returns:
        Transcribed text
    """
    client = get_groq_client()
    
    # Demo mode - return sample transcript
    if client is None:
        print("[DEMO MODE] No API key - using sample transcript")
        return DEMO_TRANSCRIPT.strip()
    
    model = os.getenv('WHISPER_MODEL', 'whisper-large-v3')
    
    # Check file size (Groq limit is 25MB)
    file_size = os.path.getsize(filepath)
    if file_size > 25 * 1024 * 1024:
        raise ValueError("Audio file too large. Maximum size is 25MB.")
    
    print(f"[GROQ] Transcribing audio with {model}...")
    
    with open(filepath, 'rb') as audio_file:
        transcription = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
            response_format="text"
        )
    
    print("[GROQ] Transcription complete!")
    return transcription


def transcribe_audio_with_timestamps(filepath: str) -> dict:
    """
    Transcribe audio with verbose output.
    
    Args:
        filepath: Path to the audio file
        
    Returns:
        Dict with text and metadata
    """
    client = get_groq_client()
    
    # Demo mode
    if client is None:
        return {
            'text': DEMO_TRANSCRIPT.strip(),
            'words': [],
            'duration': 120.0
        }
    
    model = os.getenv('WHISPER_MODEL', 'whisper-large-v3')
    
    with open(filepath, 'rb') as audio_file:
        transcription = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
            response_format="verbose_json"
        )
    
    return {
        'text': transcription.text if hasattr(transcription, 'text') else str(transcription),
        'words': [],
        'duration': transcription.duration if hasattr(transcription, 'duration') else None
    }

"""Extraction Service - LLM-based Action Item Extraction (Groq FREE)"""
import os
import json
from groq import Groq
from pydantic import BaseModel, Field
from typing import Optional

# Demo results for testing without API key
DEMO_RESULTS = {
    "summary": "Team meeting discussing project assignments and technology decisions. Key focus on authentication, database optimization, and development environment updates.",
    "decisions": [
        {
            "description": "Use PostgreSQL instead of MySQL for the new project",
            "confidence": 0.95,
            "source_text": "We've decided to use PostgreSQL instead of MySQL for the new project"
        }
    ],
    "action_items": [
        {
            "description": "Complete user authentication module",
            "owner": "John",
            "deadline": "Friday the 15th",
            "confidence": 0.92,
            "source_text": "John, you'll take care of the user authentication module. Can you have that done by next Friday?"
        },
        {
            "description": "Review database schema and propose optimizations",
            "owner": "Sarah",
            "deadline": "Wednesday",
            "confidence": 0.90,
            "source_text": "Sarah, I need you to review the database schema and propose any optimizations"
        },
        {
            "description": "Coordinate with DevOps team about staging environment",
            "owner": "Sarah",
            "deadline": None,
            "confidence": 0.75,
            "source_text": "I'll also coordinate with the DevOps team about the staging environment"
        },
        {
            "description": "Update development environment to Node 20",
            "owner": "Everyone",
            "deadline": "Before next sprint",
            "confidence": 0.88,
            "source_text": "everyone should update their development environment to Node 20"
        },
        {
            "description": "Send out setup instructions",
            "owner": None,
            "deadline": "Tomorrow",
            "confidence": 0.85,
            "source_text": "I'll send out the setup instructions by tomorrow"
        }
    ]
}

def get_groq_client():
    """Get Groq client for free LLM extraction."""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        return None  # Return None for demo mode
    return Groq(api_key=api_key)


# Pydantic models for structured output
class ActionItem(BaseModel):
    description: str = Field(description="Clear description of the action item")
    owner: Optional[str] = Field(None, description="Person responsible for this action")
    deadline: Optional[str] = Field(None, description="Due date or deadline if mentioned")
    confidence: float = Field(description="Confidence score between 0 and 1")
    source_text: str = Field(description="Original text from transcript that led to this extraction")


class Decision(BaseModel):
    description: str = Field(description="The decision that was made")
    confidence: float = Field(description="Confidence score between 0 and 1")
    source_text: str = Field(description="Original text from transcript")


class MeetingMinutes(BaseModel):
    summary: str = Field(description="Brief 2-3 sentence summary of the meeting")
    decisions: list[Decision] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)


EXTRACTION_PROMPT = """You are an expert meeting analyst. Analyze the following meeting transcript and extract:

1. A brief summary (2-3 sentences)
2. Key decisions made during the meeting
3. Action items with:
   - Clear description of what needs to be done
   - Owner (if mentioned)
   - Deadline (if mentioned)
   - Confidence score (0-1) based on how clearly this was stated
   - Source text from the transcript

Be conservative - only extract items you're confident about. Use lower confidence scores (0.5-0.7) for implied action items, and higher scores (0.8-1.0) for explicitly stated ones.

TRANSCRIPT:
{transcript}

Respond with a valid JSON object matching the schema.
"""


def extract_action_items(transcript: str) -> dict:
    """
    Extract action items and decisions from meeting transcript.
    Falls back to demo mode if no API key.
    
    Args:
        transcript: The meeting transcript text
        
    Returns:
        Dict with summary, decisions, and action_items
    """
    client = get_groq_client()
    
    # Demo mode - return sample results
    if client is None:
        print("[DEMO MODE] No API key - using sample extraction results")
        return DEMO_RESULTS
    
    model = os.getenv('GPT_MODEL', 'llama-3.3-70b-versatile')
    
    print(f"[GROQ] Extracting action items with {model}...")
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a precise meeting analyst. Extract action items and decisions from transcripts. Always respond with valid JSON only, no markdown."
            },
            {
                "role": "user",
                "content": EXTRACTION_PROMPT.format(transcript=transcript)
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    
    print("[GROQ] Extraction complete!")
    
    result = json.loads(response.choices[0].message.content)
    
    # Validate and ensure structure
    return {
        'summary': result.get('summary', ''),
        'decisions': result.get('decisions', []),
        'action_items': result.get('action_items', [])
    }


def extract_with_validation(transcript: str) -> MeetingMinutes:
    """
    Extract with Pydantic validation for type safety.
    
    Args:
        transcript: The meeting transcript text
        
    Returns:
        MeetingMinutes model instance
    """
    raw_result = extract_action_items(transcript)
    return MeetingMinutes(**raw_result)

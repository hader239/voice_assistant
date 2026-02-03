"""OpenAI-based transcript classification."""

import os
import json
from openai import OpenAI

from .models import ClassificationResult


def get_openai_client() -> OpenAI:
    """Get OpenAI client (lazy initialization)."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return OpenAI(api_key=api_key)

SYSTEM_PROMPT = """You are a helpful assistant that classifies voice transcripts into categories and extracts structured information.

Analyze the transcript and determine which category it belongs to:
- "idea": Creative ideas, concepts, thoughts, brainstorming, suggestions
- "task": Things to do, reminders, action items, errands
- "appointment": Meetings, scheduled events, calls with specific times/dates
- "spending": Financial entries, purchases, expenses, money spent

Extract a clear, concise title and a description from the transcript.

Respond with a JSON object containing:
- category: one of "idea", "task", "appointment", "spending"
- title: a short, clear title (max 50 characters)
- description: the main content/details from the transcript

Example input: "I just had this amazing idea for an app that helps people track their water intake"
Example output: {"category": "idea", "title": "Water tracking app", "description": "An app that helps people track their water intake"}

Example input: "I need to buy groceries tomorrow and also pick up the dry cleaning"
Example output: {"category": "task", "title": "Buy groceries and pick up dry cleaning", "description": "Need to buy groceries tomorrow and pick up the dry cleaning"}
"""


async def classify_transcript(text: str) -> ClassificationResult:
    """
    Classify a voice transcript using OpenAI GPT-4o-mini.
    
    Args:
        text: The voice transcript to classify
        
    Returns:
        ClassificationResult with category, title, and description
    """
    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"},
        temperature=0.3,  # Lower temperature for more consistent classification
        max_tokens=200
    )
    
    result = json.loads(response.choices[0].message.content)
    
    return ClassificationResult(
        category=result.get("category", "idea"),
        title=result.get("title", "Untitled"),
        description=result.get("description", text)
    )

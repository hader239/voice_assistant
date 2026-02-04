"""OpenAI-based transcript classification."""

import os
import json
import logging
from datetime import datetime
from openai import OpenAI

from .models import ClassificationResult

logger = logging.getLogger(__name__)

# Get today's date and time for context
def get_today():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

SYSTEM_PROMPT = """You are a helpful assistant that classifies voice transcripts into categories and extracts structured information.

Analyze the transcript and determine which category it belongs to:
- "idea": Creative ideas, concepts, thoughts, brainstorming, suggestions
- "task": Things to do, reminders, action items, errands
- "appointment": Meetings, scheduled events, calls with specific times/dates
- "spending": Financial entries, purchases, expenses, money spent
- "unsorted": Anything that doesn't fit into the above categories

Extract a clear, concise title and a description from the transcript.

For "appointment" entries: Extract the date AND time mentioned (e.g., "tomorrow at 3pm", "next Monday at 10:00") and convert it to ISO format (YYYY-MM-DDTHH:MM:SS). Today's date and time is {today}. If no specific time is mentioned, default to 09:00:00.

For "spending" entries: Extract the amount spent as a number (e.g., "50 euros" → 50, "twenty dollars" → 20).

You MUST respond with ONLY a valid JSON object (no markdown, no explanation) containing:
- category: one of "idea", "task", "appointment", "spending", "unsorted"
- title: a short, clear title (max 50 characters)
- description: the main content and details from the transcript
- date: ISO datetime string (YYYY-MM-DDTHH:MM:SS) ONLY for appointments, otherwise null
- amount: number ONLY for spending entries, otherwise null

Example responses:
{{"category": "task", "title": "Call mom", "description": "Need to call mom tomorrow", "date": null, "amount": null}}
{{"category": "appointment", "title": "Doctor visit", "description": "Annual checkup at Dr. Smith", "date": "2026-02-05T14:30:00", "amount": null}}
{{"category": "spending", "title": "Groceries", "description": "Bought groceries at the store", "date": null, "amount": 45.50}}
"""

# Cached client
_client = None


def get_client() -> OpenAI:
    """Get OpenAI client (with caching)."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment!")
            raise ValueError("OPENAI_API_KEY not set")
        logger.info(f"OpenAI API key loaded: {api_key[:8]}...{api_key[-4:]}")
        _client = OpenAI(api_key=api_key)
    return _client


async def classify_transcript(text: str) -> ClassificationResult:
    """Classify a voice transcript using OpenAI."""
    logger.info(f"Classifying transcript: {text[:100]}...")
    
    # Format prompt with today's date
    prompt = SYSTEM_PROMPT.format(today=get_today())
    input_with_hint = f"Please classify this transcript and respond with JSON: {text}"
    
    response = get_client().responses.create(
        model="gpt-5-mini-2025-08-07",
        instructions=prompt,
        input=input_with_hint,
        text={"format": {"type": "json_object"}}
    )
    
    result = json.loads(response.output_text)
    logger.info(f"Parsed result: {result}")
    
    return ClassificationResult(
        category=result.get("category", "unsorted"),
        title=result.get("title", "Untitled"),
        description=result.get("description", text),
        date=result.get("date"),
        amount=result.get("amount")
    )

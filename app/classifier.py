"""OpenAI-based transcript classification."""

import os
import json
import logging
from openai import OpenAI

from .models import ClassificationResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful assistant that classifies voice transcripts into categories and extracts structured information.

Analyze the transcript and determine which category it belongs to:
- "idea": Creative ideas, concepts, thoughts, brainstorming, suggestions
- "task": Things to do, reminders, action items, errands
- "appointment": Meetings, scheduled events, calls with specific times/dates
- "spending": Financial entries, purchases, expenses, money spent
- "unsorted": Anything that doesn't fit into the above categories

Extract a clear, concise title and a description from the transcript.

You MUST respond with ONLY a valid JSON object (no markdown, no explanation) containing:
- category: one of "idea", "task", "appointment", "spending", "unsorted"
- title: a short, clear title (max 50 characters)
- description: the main content and details from the transcript


Example response: {"category": "task", "title": "Call mom", "description": "Need to call mom tomorrow"}
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
    
    input_with_hint = f"Please classify this transcript and respond with JSON: {text}"
    
    response = get_client().responses.create(
        model="gpt-5-mini-2025-08-07",
        instructions=SYSTEM_PROMPT,
        input=input_with_hint,
        text={"format": {"type": "json_object"}}
    )
    
    result = json.loads(response.output_text)
    logger.info(f"Parsed result: {result}")
    
    return ClassificationResult(
        category=result.get("category", "idea"),
        title=result.get("title", "Untitled"),
        description=result.get("description", text)
    )

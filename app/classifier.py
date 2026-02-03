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

Extract a clear, concise title and a description from the transcript.

You MUST respond with ONLY a valid JSON object (no markdown, no explanation) containing:
- category: one of "idea", "task", "appointment", "spending"
- title: a short, clear title (max 50 characters)
- description: the main content/details from the transcript

Example response: {"category": "task", "title": "Call mom", "description": "Need to call mom tomorrow"}
"""


def get_client():
    api_key = os.getenv("OPENAI_API_KEY") 
    if api_key:
        logger.info(f"OpenAI API key loaded: {api_key[:8]}...{api_key[-4:]}")
    else:
        logger.error("OPENAI_API_KEY not found in environment!")
    _client = OpenAI()
    if _client.api_key is None:
        logger.error("OpenAI key not initialized")
        raise ValueError("OpenAI key not initialized")
    else:
        logger.info("OpenAI key initialized")
    return _client


async def classify_transcript(text: str) -> ClassificationResult:
    """
    Classify a voice transcript using OpenAI.
    """
    logger.info(f"Classifying transcript: {text[:100]}...")
    
    # Add JSON hint to input to satisfy json_object format requirement
    input_with_hint = f"Please classify this transcript and respond with JSON: {text}"
    _client = get_client()
    logger.info("Client initialized, sending request to OpenAI")
    response = _client.responses.create(
        model="gpt-5-mini-2025-08-07",
        instructions=SYSTEM_PROMPT,
        input=input_with_hint,
        text={"format": {"type": "json_object"}}
    )
    
    result = json.loads(response.output_text)
    logger.info(f"Parsed result: {result}")
    
    return ClassificationResult(
        category=result.get("category", "Unsorted"),
        title=result.get("title", "Untitled"),
        description=result.get("description", text)
    )

"""FastAPI application for Voice Assistant backend."""

import logging
from fastapi import FastAPI, HTTPException, Header
from dotenv import load_dotenv

from .models import TranscriptRequest, APIResponse
from .auth import get_user_config
from .classifier import classify_transcript
from .notion_client import save_entry
from .debug import router as debug_router

# Load environment variables from .env file (for local development)
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Voice Assistant API",
    description="Backend for iOS Shortcut that classifies voice transcripts and saves them to Notion",
    version="1.0.0"
)

# Include debug/health endpoints
app.include_router(debug_router)


@app.post("/process", response_model=APIResponse)
async def process_transcript(
    request: TranscriptRequest,
    x_api_key: str = Header(..., description="User API key for authentication")
):
    """Process a voice transcript."""
    # 1. Authenticate user
    user = get_user_config(x_api_key)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    logger.info(f"Processing transcript for user: {user.name}")
    if (request.text == ""):
        logger.error("Empty transcript")
        return APIResponse(
            success=False,
            message="Empty transcript"
        )
    # 2. Classify the transcript
    try:
        classification = await classify_transcript(request.text)
        logger.info(f"Classified as: {classification.category} - {classification.title}")
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        return APIResponse(
            success=False,
            message="Failed to classify transcript"
        )
    
    # 3. Save to Notion
    success = await save_entry(
        database_id=user.notion_database_id,
        category=classification.category,
        title=classification.title,
        description=classification.description,
        date=classification.date,
        amount=classification.amount
    )
    
    if not success:
        logger.error("Failed to save to Notion")
        return APIResponse(
            success=False,
            message="Failed to save to Notion"
        )
    
    # 4. Return confirmation
    return APIResponse(
        success=True,
        message=f"Saved {classification.category}: {classification.title}"
    )

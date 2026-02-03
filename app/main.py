"""FastAPI application for Voice Assistant backend."""

import logging
from fastapi import FastAPI, HTTPException, Header
from dotenv import load_dotenv

from .models import TranscriptRequest, APIResponse
from .auth import get_user_config
from .classifier import classify_transcript
from .notion_client import save_idea, save_task, save_appointment, save_spending

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


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway."""
    return {"status": "healthy"}


@app.get("/health/openai")
async def openai_health_check():
    """Test OpenAI API connectivity."""
    from .classifier import get_client
    try:
        client = get_client()
        models = client.models.list()
        return {"status": "connected", "models_available": len(models.data)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/debug/network")
async def debug_network():
    """Debug network connectivity to OpenAI."""
    import socket
    import ssl
    
    results = {}
    
    # Test DNS resolution
    try:
        ip = socket.gethostbyname("api.openai.com")
        results["dns"] = {"status": "ok", "ip": ip}
    except Exception as e:
        results["dns"] = {"status": "error", "error": str(e)}
    
    # Test TCP connection to port 443
    try:
        sock = socket.create_connection(("api.openai.com", 443), timeout=10)
        results["tcp"] = {"status": "ok"}
        
        # Test TLS handshake
        try:
            context = ssl.create_default_context()
            with context.wrap_socket(sock, server_hostname="api.openai.com") as ssock:
                results["tls"] = {"status": "ok", "version": ssock.version()}
        except Exception as e:
            results["tls"] = {"status": "error", "error": str(e)}
        finally:
            sock.close()
    except Exception as e:
        results["tcp"] = {"status": "error", "error": str(e)}
    
    return results


@app.post("/process", response_model=APIResponse)
async def process_transcript(
    request: TranscriptRequest,
    x_api_key: str = Header(..., description="User API key for authentication")
):
    """
    Process a voice transcript.
    
    1. Authenticate user by API key
    2. Classify the transcript using OpenAI
    3. Save to user's Notion database
    4. Return confirmation
    """
    # 1. Authenticate user
    user = get_user_config(x_api_key)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    logger.info(f"Processing transcript for user: {user.name}")
    
    # 2. Classify the transcript
    try:
        classification = await classify_transcript(request.text)
        logger.info(f"Classified as: {classification.category} - {classification.title}")
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to classify transcript")
    
    # 3. Save to Notion based on category
    save_functions = {
        "idea": save_idea,
        "task": save_task,
        "appointment": save_appointment,
        "spending": save_spending
    }
    
    save_func = save_functions.get(classification.category, save_idea)
    success = await save_func(
        database_id=user.notion_database_id,
        title=classification.title,
        description=classification.description
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save to Notion")
    
    # 4. Return confirmation
    return APIResponse(
        success=True,
        message=f"Saved {classification.category}: {classification.title}"
    )

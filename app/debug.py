"""Debug and health check endpoints for testing."""

import os
import socket
import ssl
import httpx

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint for Railway."""
    return {"status": "healthy"}


@router.get("/health/openai")
async def openai_health_check():
    """Test OpenAI API connectivity."""
    from .classifier import get_client
    try:
        client = get_client()
        models = client.models.list()
        return {"status": "connected", "models_available": len(models.data)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/debug/network")
async def debug_network():
    """Debug network connectivity to OpenAI."""
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
    
    # Test HTTP GET request
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get("https://api.openai.com/v1/models")
            results["http_get"] = {"status": "ok", "code": resp.status_code}
    except Exception as e:
        results["http_get"] = {"status": "error", "error": str(e), "type": type(e).__name__}
    
    # Test HTTP POST request
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                "https://api.openai.com/v1/responses",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": "gpt-4o-mini", "input": "test"}
            )
            results["http_post"] = {"status": "ok", "code": resp.status_code}
    except Exception as e:
        results["http_post"] = {"status": "error", "error": str(e), "type": type(e).__name__}
    
    return results

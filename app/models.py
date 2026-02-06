"""Pydantic models for the Voice Assistant API."""

from pydantic import BaseModel
from typing import Literal, Optional


class TranscriptRequest(BaseModel):
    """Request body from iOS Shortcut containing the voice transcript."""
    text: str


class ClassificationResult(BaseModel):
    """Result from OpenAI classification."""
    category: Literal["idea", "task", "appointment", "spending", "unsorted"]
    title: str
    description: str
    date: Optional[str] = None  # ISO date for appointments (YYYY-MM-DD)
    amount: Optional[float] = None  # Amount for spending entries


class UserConfig(BaseModel):
    """User configuration from users.json."""
    name: str
    notion_database_id: str
    notion_secret: str


class APIResponse(BaseModel):
    """Response sent back to iOS Shortcut."""
    success: bool
    message: str
    

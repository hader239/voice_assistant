"""Pydantic models for the Voice Assistant API."""

from pydantic import BaseModel
from typing import Literal


class TranscriptRequest(BaseModel):
    """Request body from iOS Shortcut containing the voice transcript."""
    text: str


class ClassificationResult(BaseModel):
    """Result from OpenAI classification."""
    category: Literal["idea", "task", "appointment", "spending"]
    title: str
    description: str


class UserConfig(BaseModel):
    """User configuration from users.json."""
    name: str
    notion_database_id: str


class APIResponse(BaseModel):
    """Response sent back to iOS Shortcut."""
    success: bool
    message: str

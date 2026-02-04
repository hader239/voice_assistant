"""Notion API integration for storing entries."""

import os
import logging
from typing import Optional
from notion_client import Client

logger = logging.getLogger(__name__)

# Cached client
_client = None


def get_client() -> Client:
    """Get Notion client (with caching)."""
    global _client
    if _client is None:
        _client = Client(auth=os.getenv("NOTION_API_KEY"))
    return _client


async def save_entry(
    database_id: str,
    category: str,
    title: str,
    description: str,
    date: Optional[str] = None,
    amount: Optional[float] = None
) -> bool:
    """Save an entry to Notion."""
    try:
        # Build properties
        properties = {
            "Name": {"title": [{"text": {"content": title}}]},
            "Type": {"select": {"name": category.capitalize()}},
            "Checkbox": {"checkbox": False}, # Always false
            "Description": {"rich_text": [{"text": {"content": description}}]}
        }
        
        # Add date for appointments
        if date:
            properties["Date"] = {"date": {"start": date}}
        
        # Add amount for spending
        if amount is not None:
            properties["Amount"] = {"number": amount}
        
        get_client().pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        logger.info(f"Saved {category} to Notion: {title}")
        return True
    except Exception as e:
        logger.error(f"Failed to save to Notion: {e}")
        return False

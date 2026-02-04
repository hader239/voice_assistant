"""Notion API integration for storing entries."""

import os
import logging
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


async def save_entry(database_id: str, category: str, title: str, description: str) -> bool:
    """Save an entry to Notion."""
    try:
        get_client().pages.create(
            parent={"database_id": database_id},
            properties={
                "Name": {"title": [{"text": {"content": title}}]},
                "Type": {"select": {"name": category.capitalize()}}
            },
            children=[{
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": description}}]
                }
            }]
        )
        logger.info(f"Saved {category} to Notion: {title}")
        return True
    except Exception as e:
        logger.error(f"Failed to save to Notion: {e}")
        return False

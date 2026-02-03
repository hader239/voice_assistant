"""Notion API integration for storing entries."""

import os
import logging
from notion_client import Client

logger = logging.getLogger(__name__)

# Lazy-loaded Notion client
_client = None


def get_client() -> Client:
    """Get Notion client (lazy initialization)."""
    global _client
    if _client is None:
        _client = Client(auth=os.getenv("NOTION_API_KEY"))
    return _client


async def save_entry(database_id: str, category: str, title: str, description: str) -> bool:
    """
    Save an entry to Notion.
    
    Args:
        database_id: The Notion database ID
        category: Entry type (idea, task, appointment, spending)
        title: Entry title
        description: Entry description
        
    Returns:
        True if successful, False otherwise
    """
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


# Simple wrappers for compatibility with main.py
async def save_idea(database_id: str, title: str, description: str) -> bool:
    return await save_entry(database_id, "idea", title, description)

async def save_task(database_id: str, title: str, description: str) -> bool:
    return await save_entry(database_id, "task", title, description)

async def save_appointment(database_id: str, title: str, description: str) -> bool:
    return await save_entry(database_id, "appointment", title, description)

async def save_spending(database_id: str, title: str, description: str) -> bool:
    return await save_entry(database_id, "spending", title, description)

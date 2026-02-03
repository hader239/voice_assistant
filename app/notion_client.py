"""Notion API integration for storing entries."""

import os
import logging
from notion_client import Client

logger = logging.getLogger(__name__)

# Lazy-loaded Notion client
_notion_client = None


def get_notion_client() -> Client:
    """Get Notion client (lazy initialization)."""
    global _notion_client
    if _notion_client is None:
        api_key = os.getenv("NOTION_API_KEY")
        if not api_key:
            raise ValueError("NOTION_API_KEY environment variable is not set")
        _notion_client = Client(auth=api_key)
    return _notion_client


async def save_idea(database_id: str, title: str, description: str) -> bool:
    """
    Save an idea to the user's Notion database.
    
    Args:
        database_id: The Notion database ID to save to
        title: The idea title
        description: The idea description
        
    Returns:
        True if successful, False otherwise
    """
    try:
        get_notion_client().pages.create(
            parent={"database_id": database_id},
            properties={
                "Name": {
                    "title": [{"text": {"content": title}}]
                },
                "Type": {
                    "select": {"name": "Idea"}
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": description}}]
                    }
                }
            ]
        )
        return True
    except Exception as e:
        logger.error(f"Failed to save idea to Notion: {e}")
        return False


async def save_task(database_id: str, title: str, description: str) -> bool:
    """
    Save a task to the user's Notion database.
    
    Args:
        database_id: The Notion database ID to save to
        title: The task title
        description: The task description
        
    Returns:
        True if successful, False otherwise
    """
    try:
        get_notion_client().pages.create(
            parent={"database_id": database_id},
            properties={
                "Name": {
                    "title": [{"text": {"content": title}}]
                },
                "Type": {
                    "select": {"name": "Task"}
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": description}}]
                    }
                }
            ]
        )
        return True
    except Exception as e:
        logger.error(f"Failed to save task to Notion: {e}")
        return False


async def save_appointment(database_id: str, title: str, description: str) -> bool:
    """
    Save an appointment to the user's Notion database.
    
    NOTE: This is a dummy implementation for future development.
    In the future, this should extract date, time, and attendees.
    
    Args:
        database_id: The Notion database ID to save to
        title: The appointment title
        description: The appointment description
        
    Returns:
        True (always succeeds for now)
    """
    logger.info(f"[DUMMY] Would save appointment: {title} - {description}")
    # TODO: Implement appointment extraction (date, time, person)
    # For now, save as a regular entry
    try:
        get_notion_client().pages.create(
            parent={"database_id": database_id},
            properties={
                "Name": {
                    "title": [{"text": {"content": title}}]
                },
                "Type": {
                    "select": {"name": "Appointment"}
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": description}}]
                    }
                }
            ]
        )
        return True
    except Exception as e:
        logger.error(f"Failed to save appointment to Notion: {e}")
        return False


async def save_spending(database_id: str, title: str, description: str) -> bool:
    """
    Save a spending entry to the user's Notion database.
    
    NOTE: This is a dummy implementation for future development.
    In the future, this should extract amount, currency, and category.
    
    Args:
        database_id: The Notion database ID to save to
        title: The spending title
        description: The spending description
        
    Returns:
        True (always succeeds for now)
    """
    logger.info(f"[DUMMY] Would save spending: {title} - {description}")
    # TODO: Implement spending extraction (amount, currency, category)
    # For now, save as a regular entry
    try:
        get_notion_client().pages.create(
            parent={"database_id": database_id},
            properties={
                "Name": {
                    "title": [{"text": {"content": title}}]
                },
                "Type": {
                    "select": {"name": "Spending"}
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": description}}]
                    }
                }
            ]
        )
        return True
    except Exception as e:
        logger.error(f"Failed to save spending to Notion: {e}")
        return False

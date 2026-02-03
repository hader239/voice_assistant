"""User authentication and configuration lookup."""

import json
from pathlib import Path
from typing import Optional

from .models import UserConfig


# Load users configuration from JSON file
USERS_FILE = Path(__file__).parent.parent / "users.json"


def load_users() -> dict:
    """Load users configuration from users.json."""
    if not USERS_FILE.exists():
        return {"users": {}}
    
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def get_user_config(api_key: str) -> Optional[UserConfig]:
    """
    Look up user configuration by API key.
    
    Args:
        api_key: The API key from the request header
        
    Returns:
        UserConfig if found, None otherwise
    """
    users_data = load_users()
    user_data = users_data.get("users", {}).get(api_key)
    
    if user_data is None:
        return None
    
    return UserConfig(**user_data)

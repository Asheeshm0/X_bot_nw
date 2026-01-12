import json
import os
from difflib import SequenceMatcher
from config import SIMILARITY_THRESHOLD, POSTED_FILE

def _load_titles():
    """Load posted titles from JSON file."""
    if not os.path.exists(POSTED_FILE):
        return []

    try:
        with open(POSTED_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []

def _save_titles(titles):
    with open(POSTED_FILE, "w") as f:
        json.dump(titles, f)

def _similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def is_duplicate(new_title: str) -> bool:
    """
    Checks similarity of new_title against stored titles.
    """
    old_titles = _load_titles()
    for t in old_titles:
        if _similar(new_title, t) >= SIMILARITY_THRESHOLD:
            return True
    return False

def mark_posted(title: str):
    """
    Stores a title in posted.json.
    """
    titles = _load_titles()
    titles.append(title)

    # keep file small
    if len(titles) > 100:
        titles = titles[-100:]

    _save_titles(titles)

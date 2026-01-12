import json
import os
from difflib import SequenceMatcher
from config import POSTED_FILE, SIMILARITY_THRESHOLD

def _load():
    if not os.path.exists(POSTED_FILE):
        return []
    try:
        with open(POSTED_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def is_duplicate(title):
    for old in _load():
        if SequenceMatcher(None, title.lower(), old.lower()).ratio() >= SIMILARITY_THRESHOLD:
            return True
    return False

def mark_posted(title):
    data = _load()
    data.append(title)
    data = data[-100:]
    with open(POSTED_FILE, "w") as f:
        json.dump(data, f)

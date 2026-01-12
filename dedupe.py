import hashlib
from difflib import SequenceMatcher
from config import SIMILARITY_THRESHOLD

def hash_title(title):
    return hashlib.sha256(title.lower().encode()).hexdigest()

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def is_duplicate(new_title, old_titles):
    for t in old_titles:
        if similar(new_title, t) >= SIMILARITY_THRESHOLD:
            return True
    return False
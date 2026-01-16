import feedparser
import random
import re
from config import NEWS_SOURCES


# ---------------- UTILS ----------------
def clean_html(text):
    """Remove HTML tags from RSS summaries."""
    if not text:
        return ""
    text = re.sub("<.*?>", "", text)
    return text.strip()


# ---------------- CATEGORY PRIORITY ----------------
CATEGORY_PRIORITY = [
    "India",
    "Politics",
    "World",
    "Economy"
]


# ---------------- FETCH MULTIPLE NEWS ----------------
def get_news_batch(limit=5):
    """
    Fetch multiple news items for comparison.
    Priority order:
    India → Politics → World → Economy
    """

    collected = []

    # Sort sources by priority
    sources = list(NEWS_SOURCES.items())
    sources.sort(
        key=lambda x: CATEGORY_PRIORITY.index(x[0])
        if x[0] in CATEGORY_PRIORITY else 99
    )

    for category, urls in sources:

        # ---------- SAFETY FIX ----------
        # If someone accidentally puts a string in config
        if isinstance(urls, str):
            urls = [urls]
        # --------------------------------

        random.shuffle(urls)

        for url in urls:
            try:
                feed = feedparser.parse(url)
            except Exception as e:
                print(f"Feed error ({url}): {e}")
                continue

            for entry in feed.entries:
                title = entry.get("title", "").strip()
                summary = clean_html(entry.get("summary", ""))

                # Skip weak / useless content
                if len(title) < 30 or len(summary) < 60:
                    continue

                collected.append({
                    "title": title,
                    "summary": summary,
                    "category": category
                })

                if len(collected) >= limit:
                    return collected

    return collected

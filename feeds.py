import feedparser
import random
import re
from config import NEWS_SOURCES

# ---------------- UTILS ----------------
def clean_html(text):
    if not text:
        return ""
    text = re.sub("<.*?>", "", text)
    return text.strip()

# ---------------- CATEGORY PRIORITY ----------------
CATEGORY_PRIORITY = [
    "India",
    "Politics",
    "World",
    "Global",
    "Economy"
]

# ---------------- FETCH MULTIPLE NEWS ----------------
def get_news_batch(limit=5):
    """
    Fetches multiple news items for comparison.
    Priority: Indian → Politics → Global
    Returns a list of dicts.
    """

    collected = []

    # Shuffle sources but keep category priority
    sources = list(NEWS_SOURCES.items())
    sources.sort(key=lambda x: CATEGORY_PRIORITY.index(x[0])
                 if x[0] in CATEGORY_PRIORITY else 99)

    for category, urls in sources:
        random.shuffle(urls)

        for url in urls:
            feed = feedparser.parse(url)

            for entry in feed.entries:
                title = entry.get("title", "").strip()
                summary = clean_html(entry.get("summary", ""))

                # Skip weak content
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

import feedparser
from config import NEWS_SOURCES
from dedupe import is_duplicate

def fetch_news():
    collected = []

    for source, url in NEWS_SOURCES.items():
        feed = feedparser.parse(url)
        for e in feed.entries[:5]:
            collected.append({
                "source": source,
                "title": e.title.strip(),
                "summary": getattr(e, "summary", "")[:500]
            })

    return collected

def group_similar_news(items):
    groups = []

    for item in items:
        placed = False
        for group in groups:
            if is_duplicate(item["title"], [g["title"] for g in group]):
                group.append(item)
                placed = True
                break
        if not placed:
            groups.append([item])

    return groups
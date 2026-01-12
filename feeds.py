import feedparser
import re
import random

FEEDS = {
    "TECH": ["https://www.theverge.com/rss/index.xml"],
    "POLITICS": ["https://feeds.reuters.com/Reuters/politicsNews"],
    "FINANCE": ["https://feeds.reuters.com/reuters/businessNews"],
    "WORLD": ["https://feeds.reuters.com/Reuters/worldNews"]
}

def clean(text):
    return re.sub("<.*?>", "", text or "").strip()

def get_news(limit=10):
    articles = []
    for cat, urls in FEEDS.items():
        for url in urls:
            feed = feedparser.parse(url)
            for e in feed.entries[:limit]:
                articles.append({
                    "title": clean(e.title),
                    "summary": clean(getattr(e, "summary", "")),
                    "url": e.link,
                    "category": cat
                })
    random.shuffle(articles)
    return articles

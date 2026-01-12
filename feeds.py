import feedparser
import random

# ---------------- FEED SOURCES ----------------
FEEDS = {
    "NEWS": [
        "https://feeds.reuters.com/reuters/topNews",
        "https://www.bbc.com/news/rss.xml"
    ],
    "TECH": [
        "https://feeds.feedburner.com/TechCrunch/",
        "https://www.theverge.com/rss/index.xml"
    ],
    "FINANCE": [
        "https://feeds.reuters.com/reuters/businessNews",
        "https://www.cnbc.com/id/10001147/device/rss/rss.html"
    ]
}

# ---------------- MAIN FETCHER ----------------
def get_news():
    """
    Returns a dict:
    {
        title, summary, url, category
    }
    """

    categories = list(FEEDS.keys())
    random.shuffle(categories)

    for category in categories:
        urls = FEEDS[category]
        random.shuffle(urls)

        for url in urls:
            feed = feedparser.parse(url)

            for entry in feed.entries[:5]:
                title = getattr(entry, "title", "").strip()
                summary = getattr(entry, "summary", "").strip()
                link = getattr(entry, "link", "").strip()

                if title and link:
                    return {
                        "title": title,
                        "summary": summary,
                        "url": link,
                        "category": category
                    }

    return None

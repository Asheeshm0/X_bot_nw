# feeds.py
import feedparser
import re
from difflib import SequenceMatcher
from collections import defaultdict

# ---------- SOURCES ----------
FEEDS = {
    "INDIA": [
        "https://feeds.reuters.com/reuters/INnews",
        "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml",
        "https://www.thehindu.com/news/national/feeder/default.rss"
    ],
    "WORLD": [
        "https://feeds.reuters.com/Reuters/worldNews",
        "https://feeds.bbci.co.uk/news/world/rss.xml"
    ],
    "POLITICS": [
        "https://feeds.reuters.com/Reuters/politicsNews"
    ]
}

# ---------- KEYWORDS ----------
INDIA_KEYWORDS = [
    "india", "indian", "delhi", "new delhi", "parliament",
    "lok sabha", "rajya sabha", "supreme court",
    "modi", "bjp", "congress", "election commission",
    "kashmir", "manipur", "border", "china", "pakistan"
]

IMPORTANCE_KEYWORDS = [
    "war", "attack", "election", "government", "killed",
    "ceasefire", "military", "crisis", "sanctions",
    "president", "prime minister", "parliament", "verdict"
]

# ---------- HELPERS ----------
def clean(text):
    return re.sub("<.*?>", "", text or "").strip()

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def importance_score(text):
    t = text.lower()
    score = sum(1 for k in IMPORTANCE_KEYWORDS if k in t)
    return score

def india_boost(text):
    t = text.lower()
    return sum(1 for k in INDIA_KEYWORDS if k in t)

# ---------- MAIN COMPARISON ----------
def get_compared_news(limit=20):
    raw_articles = []

    # Step 1: Collect news
    for category, urls in FEEDS.items():
        for url in urls:
            feed = feedparser.parse(url)
            for e in feed.entries[:limit]:
                raw_articles.append({
                    "title": clean(e.title),
                    "summary": clean(getattr(e, "summary", "")),
                    "category": category
                })

    if not raw_articles:
        return None

    # Step 2: Cluster similar stories
    clusters = defaultdict(list)
    for article in raw_articles:
        placed = False
        for key in clusters:
            if similarity(article["title"], key) > 0.72:
                clusters[key].append(article)
                placed = True
                break
        if not placed:
            clusters[article["title"]].append(article)

    # Step 3: Score clusters (India priority)
    ranked = []
    for cluster in clusters.values():
        combined_text = " ".join(a["title"] + " " + a["summary"] for a in cluster)

        score = 0
        score += importance_score(combined_text) * 2      # global importance
        score += india_boost(combined_text) * 4           # 🇮🇳 INDIA PRIORITY
        score += len(cluster) * 2                          # multi-source confidence

        ranked.append((score, cluster))

    ranked.sort(key=lambda x: x[0], reverse=True)

    best_cluster = ranked[0][1]

    merged_summary = " ".join(a["summary"] for a in best_cluster)[:600]

    return {
        "title": best_cluster[0]["title"],
        "summary": merged_summary,
        "category": best_cluster[0]["category"]
    }

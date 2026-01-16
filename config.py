# ---------------- BASIC CONFIG ----------------
MAX_TWEET_LEN = 280

POSTED_FILE = "posted.json"
LOG_FILE = "logs/bot.log"

# Semantic duplicate control (0.7–0.85 recommended)
SIMILARITY_THRESHOLD = 0.78


# ---------------- NEWS SOURCES ----------------
# IMPORTANT:
# Every value MUST be a list, even if it has only one URL

NEWS_SOURCES = {
    "India": [
        "https://feeds.feedburner.com/ndtvnews-top-stories",
        "https://www.thehindu.com/news/feeder/default.rss",
        "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
        "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
    ],

    "Politics": [
        "https://feeds.feedburner.com/ndtvnews-politics",
        "https://www.thehindu.com/news/national/feeder/default.rss"
    ],

    "World": [
        "https://feeds.reuters.com/reuters/topNews",
        "http://feeds.bbci.co.uk/news/rss.xml",
        "https://apnews.com/rss"
    ],

    "Economy": [
        "https://www.business-standard.com/rss/home_page_top_stories.rss"
    ]
}

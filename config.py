MAX_TWEET_LEN = 280

NEWS_SOURCES = {
    "Reuters": "https://feeds.reuters.com/reuters/topNews",
    "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
    "AP News": "https://apnews.com/rss",
    "Times of India": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "Hindustan Times": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
    "The Hindu": "https://www.thehindu.com/news/feeder/default.rss",
    "Business Standard": "https://www.business-standard.com/rss/home_page_top_stories.rss",
    "NDTV": "https://feeds.feedburner.com/ndtvnews-top-stories"
}

POSTED_FILE = "posted.json"
LOG_FILE = "logs/bot.log"

SIMILARITY_THRESHOLD = 0.78   # semantic duplicate control
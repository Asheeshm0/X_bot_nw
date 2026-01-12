import os
import json
import tweepy

from config import MAX_TWEET_LEN, POSTED_FILE
from feeds import get_news
from ai_writer import rewrite_news
from dedupe import is_duplicate, mark_posted
from banner import generate_banner

# ---------------- LOGGING ----------------
def log(msg):
    os.makedirs("logs", exist_ok=True)
    with open("logs/bot.log", "a") as f:
        f.write(msg + "\n")
    print(msg)

# ---------------- INIT ----------------
if not os.path.exists(POSTED_FILE):
    with open(POSTED_FILE, "w") as f:
        json.dump([], f)

# ---------------- X AUTH ----------------
client_v2 = tweepy.Client(
    consumer_key=os.getenv("X_API_KEY"),
    consumer_secret=os.getenv("X_API_SECRET"),
    access_token=os.getenv("X_ACCESS_TOKEN"),
    access_token_secret=os.getenv("X_ACCESS_SECRET")
)

auth = tweepy.OAuth1UserHandler(
    os.getenv("X_API_KEY"),
    os.getenv("X_API_SECRET"),
    os.getenv("X_ACCESS_TOKEN"),
    os.getenv("X_ACCESS_SECRET")
)
client_v1 = tweepy.API(auth)

# ---------------- MAIN ----------------
def run():
    log("Bot started")

    news = get_news()
    if not news:
        log("No news found")
        return

    title = news["title"]
    summary = news["summary"]
    url = news["url"]
    category = news["category"]

    if is_duplicate(title):
        log(f"Duplicate skipped: {title}")
        return

    rewritten = rewrite_news(title, summary)
    headline = rewritten.get("headline", title)
    short_summary = rewritten.get("summary", summary)

    media_ids = []
    try:
        image_path = generate_banner(
            headline=headline,
            summary=short_summary,
            category=category
        )
        media = client_v1.media_upload(image_path)
        media_ids = [media.media_id]
    except Exception as e:
        log(f"Banner generation failed: {e}")

    tweet_text = f"{headline}\n\n{url}"
    tweet_text = tweet_text[:MAX_TWEET_LEN]

    client_v2.create_tweet(
        text=tweet_text,
        media_ids=media_ids if media_ids else None
    )

    mark_posted(title)
    log(f"Posted: {headline}")

# ---------------- ENTRY ----------------
if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        log(f"ERROR: {e}")
        raise

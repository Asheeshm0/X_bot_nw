import os
import tweepy
from datetime import datetime, timedelta

from feeds import get_news_batch
from ai_writer import rewrite_news
from dedupe import is_duplicate, mark_posted
from banner import generate_banner
from config import MAX_TWEET_LEN

# ---------------- LOGGING ----------------
def log(msg):
    os.makedirs("logs", exist_ok=True)
    with open("logs/bot.log", "a") as f:
        f.write(msg + "\n")
    print(msg)

# ---------------- X AUTH ----------------
client_v2 = tweepy.Client(
    consumer_key=os.getenv("X_API_KEY"),
    consumer_secret=os.getenv("X_API_SECRET"),
    access_token=os.getenv("X_ACCESS_TOKEN"),
    access_token_secret=os.getenv("X_ACCESS_SECRET")
)

client_v1 = tweepy.API(
    tweepy.OAuth1UserHandler(
        os.getenv("X_API_KEY"),
        os.getenv("X_API_SECRET"),
        os.getenv("X_ACCESS_TOKEN"),
        os.getenv("X_ACCESS_SECRET"),
    )
)

# ---------------- POSTING WINDOW (DELAY SAFE) ----------------
POST_WINDOWS = [
    (5, 8),    # Morning
    (11, 14),  # Noon
    (18, 21),  # Evening
]

def valid_posting_time():
    now = datetime.utcnow() + timedelta(minutes=50)  # ⏱ START DELAY BUFFER
    hour = now.hour
    for start, end in POST_WINDOWS:
        if start <= hour <= end:
            return True
    return False

# ---------------- NEWS SELECTION ----------------
def select_best_news(items):
    items.sort(key=lambda x: len(x["summary"]), reverse=True)
    return items[0] if items else None

# ---------------- MAIN BOT ----------------
def run():
    log("Bot started")

    if not valid_posting_time():
        log("Not a valid posting window. Exiting safely.")
        return

    news_list = get_news_batch(limit=8)
    if not news_list:
        log("No news fetched")
        return

    best = select_best_news(news_list)
    title = best["title"]
    summary = best["summary"]
    category = best["category"]

    if is_duplicate(title):
        log("Duplicate skipped")
        return

    ai = rewrite_news(title, summary, category)

    headline = ai["headline"]
    body = ai["body"]
    hashtags = ai["hashtags"]

    # ---------- IMAGE ----------
    media_ids = []
    try:
        image_path = generate_banner(
            headline=headline,
            summary=body,
            category=category
        )
        media = client_v1.media_upload(image_path)
        media_ids = [media.media_id]
    except Exception as e:
        log(f"Banner error: {e}")

    tweet_text = f"{headline}\n\n{body}\n\n" + " ".join(hashtags)
    tweet_text = tweet_text[:MAX_TWEET_LEN]

    client_v2.create_tweet(
        text=tweet_text,
        media_ids=media_ids if media_ids else None
    )

    mark_posted(title)
    log(f"Posted successfully: {headline}")

# ---------------- ENTRY ----------------
if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        log(f"ERROR: {e}")

import os
import json
import tweepy
from datetime import datetime

from feeds import fetch_news, group_similar_news
from ai_writer import generate_best_post
from dedupe import hash_title
from config import POSTED_FILE, MAX_TWEET_LEN, LOG_FILE
from banner import generate_banner   # ✅ NEW: banner generator

# -------------------------------------------------
# Ensure required directories exist (GitHub Actions safe)
# -------------------------------------------------
os.makedirs("logs", exist_ok=True)
os.makedirs("images", exist_ok=True)

# -------------------------------------------------
# Load posted history
# -------------------------------------------------
if os.path.exists(POSTED_FILE):
    with open(POSTED_FILE, "r") as f:
        posted = set(json.load(f))
else:
    posted = set()

def save_posted():
    with open(POSTED_FILE, "w") as f:
        json.dump(list(posted), f)

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

# -------------------------------------------------
# X (Twitter) clients
# -------------------------------------------------
client_v2 = tweepy.Client(
    consumer_key=os.getenv("X_API_KEY"),
    consumer_secret=os.getenv("X_API_SECRET"),
    access_token=os.getenv("X_ACCESS_TOKEN"),
    access_token_secret=os.getenv("X_ACCESS_SECRET")
)

auth_v1 = tweepy.OAuth1UserHandler(
    os.getenv("X_API_KEY"),
    os.getenv("X_API_SECRET"),
    os.getenv("X_ACCESS_TOKEN"),
    os.getenv("X_ACCESS_SECRET")
)
client_v1 = tweepy.API(auth_v1)

# -------------------------------------------------
# Main bot logic
# -------------------------------------------------
def run():
    articles = fetch_news()
    groups = group_similar_news(articles)

    for group in groups:
        main_title = group[0]["title"]
        h = hash_title(main_title)

        # Skip if already posted
        if h in posted:
            continue

        # AI generates clean professional content
        headline, details, hashtags = generate_best_post(main_title, group)

        # Build banner image (NO API, pure PIL)
        image_path = generate_banner(
            headline=headline,
            summary=details[:220],   # keep image text short & clear
            category="NEWS"
        )

        # Upload image using v1 API
        media = client_v1.media_upload(image_path)

        # Final tweet text (clean, readable)
        tweet_text = f"{headline}\n\n{hashtags}"
        tweet_text = tweet_text[:MAX_TWEET_LEN]

        # Post tweet with image
        client_v2.create_tweet(
            text=tweet_text,
            media_ids=[media.media_id]
        )

        # Save state
        posted.add(h)
        save_posted()
        log(f"Posted with image: {headline}")

        break  # ✅ one high-quality post per run

# -------------------------------------------------
# Entry point
# -------------------------------------------------
if __name__ == "__main__":
    run()

import os
import json
import tweepy
from feeds import get_latest_news
from ai_writer import rewrite_news
from dedupe import is_duplicate, mark_posted
from banner import generate_banner

# ---------------- CONFIG ----------------
MAX_TWEET_LEN = 280
POSTED_FILE = "posted.json"

# ---------------- LOGGING ----------------
def log(msg):
    os.makedirs("logs", exist_ok=True)
    with open("logs/bot.log", "a") as f:
        f.write(msg + "\n")
    print(msg)

# ---------------- LOAD POSTED ----------------
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

# ---------------- MAIN RUN ----------------
def run():
    log("Bot started")

    # 1️⃣ Get raw news
    news = get_latest_news()
    if not news:
        log("No news fetched")
        return

    title = (news.get("title") or "").strip()
    summary = (news.get("summary") or "").strip()
    url = news.get("url")
    category = (news.get("category") or "NEWS").upper()

    if not title:
        log("Empty title, skipping")
        return

    # 2️⃣ Deduplication
    if is_duplicate(title):
        log("Duplicate news skipped")
        return

    # 3️⃣ AI rewrite (clean, simple)
    rewritten = rewrite_news(title, summary)
    headline = rewritten.get("headline", title)
    short_summary = rewritten.get("summary", summary)

    # 4️⃣ Generate premium banner
    image_path = generate_banner(
        headline=headline,
        summary=short_summary,
        category=category
    )

    # 5️⃣ Compose tweet text
    tweet_text = f"{headline}\n\n{url}" if url else headline
    tweet_text = tweet_text[:MAX_TWEET_LEN]

    # 6️⃣ Upload image + post
    media = client_v1.media_upload(image_path)
    client_v2.create_tweet(
        text=tweet_text,
        media_ids=[media.media_id]
    )

    # 7️⃣ Save posted hash
    mark_posted(title)

    log(f"Posted successfully: {headline}")

# ---------------- ENTRY ----------------
if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        log(f"ERROR: {e}")
        raise

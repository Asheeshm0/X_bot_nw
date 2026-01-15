import os
import json
import tweepy
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from feeds import get_news_batch
from ai_writer import rewrite_news
from dedupe import is_duplicate, mark_posted
from banner import generate_banner
from config import MAX_TWEET_LEN

# ---------------- TIME CONFIG ----------------
IST = ZoneInfo("Asia/Kolkata")
POST_STATE_FILE = "post_state.json"

# Posting slots (IST)
POST_SLOTS = {
    "morning": (5, 9),
    "noon": (11, 14),
    "evening": (18, 22)
}

# Allow posting even if bot starts late (minutes)
GRACE_MINUTES = 20

# ---------------- LOGGING ----------------
def log(msg):
    os.makedirs("logs", exist_ok=True)
    with open("logs/bot.log", "a") as f:
        f.write(msg + "\n")
    print(msg)

# ---------------- SLOT HELPERS ----------------
def get_current_slot():
    now = datetime.now(IST)

    for slot, (start_hour, end_hour) in POST_SLOTS.items():
        start = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end = now.replace(hour=end_hour, minute=0, second=0, microsecond=0)

        # Normal window
        if start <= now < end:
            return slot

        # Grace window after slot end
        if end <= now <= end + timedelta(minutes=GRACE_MINUTES):
            return slot

    return None

def load_post_state():
    if not os.path.exists(POST_STATE_FILE):
        return {}
    try:
        with open(POST_STATE_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def save_post_state(state):
    with open(POST_STATE_FILE, "w") as f:
        json.dump(state, f)

def already_posted_today(slot):
    today = datetime.now(IST).strftime("%Y-%m-%d")
    state = load_post_state()
    return state.get(today) == slot

def mark_posted_today(slot):
    today = datetime.now(IST).strftime("%Y-%m-%d")
    state = load_post_state()
    if not isinstance(state, dict):
        state = {}
    state[str(today)] = str(slot)
    save_post_state(state)

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

# ---------------- NEWS COMPARISON ----------------
def select_best_news(news_items):
    if not news_items:
        return None
    # Prefer longer summaries (often higher importance)
    news_items.sort(key=lambda x: len(x.get("summary", "")), reverse=True)
    return news_items[0]

# ---------------- MAIN BOT ----------------
def run():
    log("Bot started")

    # ---- TIME CHECK (WITH GRACE) ----
    slot = get_current_slot()
    if not slot:
        log("Not a valid posting time (even with grace). Exiting.")
        return

    if already_posted_today(slot):
        log(f"Already posted for {slot}. Exiting.")
        return

    # ---- FETCH & COMPARE NEWS ----
    news_list = get_news_batch(limit=5)
    if not news_list:
        log("No news found")
        return

    best_news = select_best_news(news_list)
    title = best_news["title"]
    summary = best_news["summary"]
    category = best_news["category"]

    # ---- DEDUPLICATION ----
    if is_duplicate(title):
        log("Duplicate skipped")
        return

    # ---- AI REWRITE ----
    ai = rewrite_news(title, summary, category)
    headline = ai.get("headline", title)
    body = ai.get("body", summary)
    hashtags = ai.get("hashtags", [])

    # ---- BANNER ----
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
        log(f"Banner failed: {e}")

    # ---- POST TWEET (NO LINKS) ----
    tweet_text = f"{headline}\n\n{body}\n\n" + " ".join(hashtags)
    tweet_text = tweet_text[:MAX_TWEET_LEN]

    client_v2.create_tweet(
        text=tweet_text,
        media_ids=media_ids if media_ids else None
    )

    mark_posted(title)
    mark_posted_today(slot)
    log(f"Posted ({slot}): {headline}")

# ---------------- ENTRY ----------------
if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        log(f"ERROR: {e}")

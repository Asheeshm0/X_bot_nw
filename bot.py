import os
import json
from datetime import datetime, timezone
import tweepy

from feeds import get_news_batch
from ai_writer import rewrite_news
from dedupe import is_duplicate, mark_posted
from banner import generate_banner
from config import MAX_TWEET_LEN

# ---------------- FILES ----------------
STATE_FILE = "post_state.json"

# ---------------- LOGGING ----------------
def log(msg):
    os.makedirs("logs", exist_ok=True)
    with open("logs/bot.log", "a") as f:
        f.write(msg + "\n")
    print(msg)

# ---------------- STATE HANDLING (SAFE) ----------------
def load_state():
    if not os.path.exists(STATE_FILE):
        return {"last_post": None}

    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass

    return {"last_post": None}


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# ---------------- POSTING WINDOW (DELAY SAFE) ----------------
def is_posting_window():
    """
    Allows posting in 3 broad windows (IST-safe even with delays):
    Morning: 04–08
    Noon:    10–14
    Evening: 17–21
    """
    now = datetime.now(timezone.utc)
    hour = now.hour + 5  # rough IST offset (no pytz needed)

    windows = [(4, 8), (10, 14), (17, 21)]
    return any(start <= hour <= end for start, end in windows)

# ---------------- X AUTH ----------------
client_v2 = tweepy.Client(
    consumer_key=os.getenv("X_API_KEY"),
    consumer_secret=os.getenv("X_API_SECRET"),
    access_token=os.getenv("X_ACCESS_TOKEN"),
    access_token_secret=os.getenv("X_ACCESS_SECRET"),
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
def select_best_news(items):
    """
    Picks the most important news:
    - Longer summary
    - Political / global priority
    """
    if not items:
        return None

    def score(n):
        score = len(n.get("summary", ""))
        if n.get("category", "").lower() in ["politics", "world", "india"]:
            score += 500
        return score

    items.sort(key=score, reverse=True)
    return items[0]

# ---------------- MAIN BOT ----------------
def run():
    log("Bot started")

    if not is_posting_window():
        log("Not a valid posting window. Exiting safely.")
        return

    state = load_state()

    news_list = get_news_batch(limit=6)
    if not news_list:
        log("No news found")
        return

    best = select_best_news(news_list)
    if not best:
        log("No suitable news selected")
        return

    title = best["title"]
    summary = best["summary"]
    category = best.get("category", "Politics")

    if is_duplicate(title):
        log("Duplicate skipped")
        return

    ai = rewrite_news(title, summary, category)

    headline = ai.get("headline", title)
    body = ai.get("body", summary)
    hashtags = ai.get("hashtags", [])

    # ---------------- IMAGE ----------------
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

    # ---------------- FINAL TWEET ----------------
    tweet_text = f"{headline}\n\n{body}\n\n" + " ".join(hashtags)
    tweet_text = tweet_text[:MAX_TWEET_LEN]

    client_v2.create_tweet(
        text=tweet_text,
        media_ids=media_ids if media_ids else None
    )

    mark_posted(title)
    state["last_post"] = datetime.utcnow().isoformat()
    save_state(state)

    log(f"Posted successfully: {headline}")

# ---------------- ENTRY ----------------
if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        log(f"FATAL ERROR: {e}")

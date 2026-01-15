import os
import tweepy
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

# ---------------- NEWS COMPARISON ----------------
def select_best_news(news_items):
    """
    Chooses the most important news based on length & seriousness.
    """
    if not news_items:
        return None

    # Prefer longer summaries (usually more important)
    news_items.sort(key=lambda x: len(x["summary"]), reverse=True)
    return news_items[0]

# ---------------- MAIN BOT ----------------
def run():
    log("Bot started")

    # Fetch multiple news items (comparison feature)
    news_list = get_news_batch(limit=5)

    if not news_list:
        log("No news found")
        return

    best_news = select_best_news(news_list)

    title = best_news["title"]
    summary = best_news["summary"]
    category = best_news["category"]

    # Deduplication
    if is_duplicate(title):
        log("Duplicate skipped")
        return

    # AI rewrite
    ai = rewrite_news(title, summary, category)
    headline = ai["headline"]
    body = ai["body"]
    hashtags = ai["hashtags"]

    # Banner generation
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

    # Final tweet text (NO LINKS)
    tweet_text = f"{headline}\n\n{body}\n\n" + " ".join(hashtags)
    tweet_text = tweet_text[:MAX_TWEET_LEN]

    # Post tweet
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

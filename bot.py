# bot.py
import os
import tweepy
from feeds import get_compared_news
from banner import generate_banner
from ai_writer import rewrite_news
from dedupe import is_duplicate, mark_posted
from config import MAX_TWEET_LEN

def log(msg):
    os.makedirs("logs", exist_ok=True)
    with open("logs/bot.log", "a") as f:
        f.write(msg + "\n")
    print(msg)

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
        os.getenv("X_ACCESS_SECRET")
    )
)

def run():
    news = get_compared_news()

    if not news:
        log("No news found")
        return

    title = news["title"]

    if is_duplicate(title):
        log("Duplicate skipped")
        return

    ai = rewrite_news(title, news["summary"])

    headline = ai["headline"]
    summary = ai["summary"]
    hashtags = " ".join(ai["hashtags"])

    image_path = generate_banner(headline, summary, news["category"])
    media = client_v1.media_upload(image_path)

    tweet = f"{headline}\n\n{summary}\n\n{hashtags}"
    tweet = tweet[:MAX_TWEET_LEN]

    client_v2.create_tweet(
        text=tweet,
        media_ids=[media.media_id]
    )

    mark_posted(title)
    log(f"Posted compared news: {headline}")

if __name__ == "__main__":
    run()

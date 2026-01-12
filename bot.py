import os
import tweepy
from feeds import get_news
from banner import generate_banner
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

auth = tweepy.OAuth1UserHandler(
    os.getenv("X_API_KEY"),
    os.getenv("X_API_SECRET"),
    os.getenv("X_ACCESS_TOKEN"),
    os.getenv("X_ACCESS_SECRET")
)
client_v1 = tweepy.API(auth)

def run():
    for news in get_news():
        title = news["title"]
        if is_duplicate(title):
            continue

        banner = generate_banner(
            headline=title,
            summary=news["summary"][:160],
            category=news["category"]
        )

        media = client_v1.media_upload(banner)

        tweet = f"{news['url']}"
        client_v2.create_tweet(text=tweet[:MAX_TWEET_LEN], media_ids=[media.media_id])

        mark_posted(title)
        log(f"Posted: {title}")
        break

if __name__ == "__main__":
    run()

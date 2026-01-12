import os, json, tweepy
from feeds import fetch_news, group_similar_news
from ai_writer import generate_best_post
from dedupe import hash_title
from config import POSTED_FILE, MAX_TWEET_LEN
from datetime import datetime

# Load posted history
if os.path.exists(POSTED_FILE):
    posted = set(json.load(open(POSTED_FILE)))
else:
    posted = set()

def save_posted():
    json.dump(list(posted), open(POSTED_FILE, "w"))

def log(msg):
    with open("logs/bot.log", "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

# X Client
client = tweepy.Client(
    consumer_key=os.getenv("X_API_KEY"),
    consumer_secret=os.getenv("X_API_SECRET"),
    access_token=os.getenv("X_ACCESS_TOKEN"),
    access_token_secret=os.getenv("X_ACCESS_SECRET")
)

def run():
    articles = fetch_news()
    groups = group_similar_news(articles)

    for group in groups:
        main_title = group[0]["title"]
        h = hash_title(main_title)

        if h in posted:
            continue

        headline, details, hashtags = generate_best_post(
            main_title, group
        )

        tweet = f"{headline}\n\n{details}\n\n{hashtags}"
        tweet = tweet[:MAX_TWEET_LEN]

        client.create_tweet(text=tweet)

        posted.add(h)
        save_posted()
        log(f"Posted: {headline}")
        break   # one high-quality post per run

if __name__ == "__main__":
    run()
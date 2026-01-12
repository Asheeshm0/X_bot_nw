import os
import tweepy
from feeds import get_news
from banner import generate_banner
from ai_writer import rewrite_news
from dedupe import is_duplicate, mark_posted
from config import MAX_TWEET_LEN

def log(msg):
    os.makedirs("logs", exist_ok=True)
    with open("logs/bot.log", "a") as f:
        f.write(msg + "\n")
    print(msg)

# X Auth
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

        # 🔹 Gemini rewrite
        ai = rewrite_news(title, news["summary"])

        headline = ai["headline"]
        summary = ai["summary"]
        hashtags = " ".join(ai["hashtags"])

        # 🔹 Generate banner (text ALWAYS fits)
        image_path = generate_banner(
            headline=headline,
            summary=summary,
            category=news["category"]
        )

        media = client_v1.media_upload(image_path)

        # 🔹 Main tweet (NO LINK)
        tweet_text = f"{headline}\n\n{summary}\n\n{hashtags}"
        tweet_text = tweet_text[:MAX_TWEET_LEN]

        tweet = client_v2.create_tweet(
            text=tweet_text,
            media_ids=[media.media_id]
        )

        # 🔹 Optional reply with source link (pro style)
        try:
            client_v2.create_tweet(
                text=f"Source: {news['url']}",
                in_reply_to_tweet_id=tweet.data["id"]
            )
        except:
            pass

        mark_posted(title)
        log(f"Posted: {headline}")
        break

if __name__ == "__main__":
    run()

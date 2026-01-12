import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

def generate_best_post(topic, articles):
    """
    articles = list of {source, title, summary}
    """

    context = ""
    for a in articles:
        context += f"\nSource: {a['source']}\nTitle: {a['title']}\nSummary: {a['summary']}\n"

    prompt = f"""
You are a senior editor for a top news media account on X.

TASK:
Compare multiple reports about the SAME news and write ONE best post.

RULES:
- Neutral, professional tone
- Clear English
- Headline under 180 characters
- 3 bullet points max
- Choose facts common across sources
- DO NOT repeat source names
- Generate BEST hashtags (3–5) for reach
- NO emojis in headline
- NO misinformation

NEWS CONTEXT:
{context}

RETURN EXACT FORMAT:

HEADLINE:
DETAILS:
HASHTAGS:
"""

    r = model.generate_content(prompt)
    text = r.text.strip()

    def extract(label):
        return text.split(label)[1].split("\n")[0].strip()

    headline = extract("HEADLINE:")
    details = text.split("DETAILS:")[1].split("HASHTAGS:")[0].strip()
    hashtags = extract("HASHTAGS:")

    return headline, details, hashtags
import os
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = genai.GenerativeModel("gemini-1.5-flash")

def rewrite_news(title, summary):
    """
    Returns:
    {
      headline: short clear headline,
      summary: simple 2-line summary,
      hashtags: list of hashtags
    }
    """
    prompt = f"""
You are a professional news editor.

Rewrite the following news in simple, neutral English.

RULES:
- Headline: max 90 characters
- Summary: max 2 short lines
- Easy to understand
- No emojis
- No clickbait
- Generate 4 relevant hashtags (no spam)

Return ONLY valid JSON.

TITLE:
{title}

SUMMARY:
{summary}
"""

    try:
        res = MODEL.generate_content(prompt)
        text = res.text.strip()

        # Remove markdown if Gemini adds it
        if text.startswith("```"):
            text = text.split("```")[1]

        data = json.loads(text)

        return {
            "headline": data.get("headline", title),
            "summary": data.get("summary", summary[:160]),
            "hashtags": data.get("hashtags", [])
        }

    except Exception as e:
        # SAFE FALLBACK (never crash)
        return {
            "headline": title[:90],
            "summary": summary[:160],
            "hashtags": ["#News", "#Update"]
        }

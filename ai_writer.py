import os
import json
import google.generativeai as genai

# ---------------- GEMINI SETUP ----------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- AI WRITER ----------------
def rewrite_news(title, summary, category):
    """
    ALWAYS returns:
    {
      headline: str
      body: str
      hashtags: list[str]
    }
    NEVER returns invalid types.
    """

    prompt = f"""
You are a senior editor of a large Indian news account on X (Twitter).

RULES:
- NO source links
- NO media names
- Simple language
- Indian + global political focus
- Important & public-interest news

HASHTAGS:
Generate 7–11 relevant hashtags
NO generic tags (#news #update #viral)

CATEGORY: {category}

TITLE:
{title}

SUMMARY:
{summary}

OUTPUT JSON ONLY:
{{
  "headline": "...",
  "body": "...",
  "hashtags": ["#Example1", "#Example2"]
}}
"""

    try:
        response = MODEL.generate_content(prompt)
        text = response.text.strip()

        # ---------- SAFE JSON EXTRACTION ----------
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == -1:
            raise ValueError("JSON not found")

        data = json.loads(text[start:end])

        headline = str(data.get("headline", title)).strip()
        body = str(data.get("body", summary)).strip()

        raw_tags = data.get("hashtags", [])

        # ---------- HASHTAG NORMALIZATION ----------
        clean_tags = []

        if isinstance(raw_tags, str):
            raw_tags = raw_tags.replace(",", " ").split()

        if isinstance(raw_tags, list):
            for tag in raw_tags:
                if isinstance(tag, str):
                    tag = tag.strip()
                    if not tag.startswith("#"):
                        tag = "#" + tag.replace("#", "")
                    clean_tags.append(tag)

        # ---------- GUARANTEED FALLBACK ----------
        if len(clean_tags) < 6:
            clean_tags = [
                "#India",
                "#IndianPolitics",
                "#WorldNews",
                "#GlobalAffairs",
                "#BreakingUpdates",
                "#PublicInterest",
            ]

        return {
            "headline": headline,
            "body": body,
            "hashtags": clean_tags[:11]
        }

    except Exception:
        return {
            "headline": title,
            "body": summary,
            "hashtags": [
                "#India",
                "#IndianPolitics",
                "#WorldNews",
                "#GlobalAffairs",
                "#BreakingUpdates",
                "#PublicInterest",
            ]
        }

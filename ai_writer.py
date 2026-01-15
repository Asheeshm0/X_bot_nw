import os
import json
import google.generativeai as genai

# ---------------- GEMINI SETUP ----------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- AI WRITER ----------------
def rewrite_news(title, summary, category):
    """
    Returns a dictionary:
    {
      "headline": str,
      "body": str,
      "hashtags": list[str]
    }
    ALWAYS returns valid types (never a string).
    """

    prompt = f"""
You are a senior editor of a large Indian news account on X (Twitter).

TASK:
Rewrite the news in a professional, clear, and engaging way.

STRICT RULES:
- DO NOT include any source links
- DO NOT mention websites or news agencies
- Use simple language (easy for common people)
- Focus on WHY this news matters
- Avoid technical jargon
- Prefer Indian & global political context

HASHTAGS RULES:
Generate 7–11 hashtags total:
- 2–3 trending or event-based hashtags
- 2–4 evergreen political/global hashtags
- 3–5 India / region / leader based hashtags

DO NOT use generic tags like:
#news #update #breaking #viral

CATEGORY: {category}

TITLE:
{title}

SUMMARY:
{summary}

OUTPUT FORMAT (STRICT JSON ONLY):
{{
  "headline": "Short strong headline",
  "body": "2–3 simple sentences explaining the news clearly.",
  "hashtags": ["#ExampleTag1", "#ExampleTag2"]
}}
"""

    try:
        response = MODEL.generate_content(prompt)
        text = response.text.strip()

        # ---- SAFE JSON EXTRACTION ----
        start = text.find("{")
        end = text.rfind("}") + 1

        if start == -1 or end == -1:
            raise ValueError("No JSON found")

        data = json.loads(text[start:end])

        headline = str(data.get("headline", title)).strip()
        body = str(data.get("body", summary)).strip()

        hashtags = data.get("hashtags", [])
        if not isinstance(hashtags, list):
            hashtags = []

        # Clean hashtags
        clean_tags = []
        for tag in hashtags:
            if isinstance(tag, str) and tag.startswith("#"):
                clean_tags.append(tag.strip())

        # Minimum hashtag fallback
        if len(clean_tags) < 5:
            clean_tags = [
                "#India",
                "#Politics",
                "#WorldNews",
                "#GlobalAffairs",
                "#PublicInterest"
            ]

        return {
            "headline": headline,
            "body": body,
            "hashtags": clean_tags[:11]
        }

    except Exception as e:
        # -------- SAFE FALLBACK (NEVER CRASH) --------
        return {
            "headline": title,
            "body": summary,
            "hashtags": [
                "#India",
                "#Politics",
                "#WorldNews",
                "#GlobalAffairs",
                "#PublicInterest"
            ]
        }

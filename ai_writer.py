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
      headline: str,
      body: str,
      hashtags: list[str]
    }
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
- Avoid tech-heavy language
- Prefer Indian & global political context

HASHTAGS:
Generate 7–11 hashtags total:
- 2–3 trending / event-based hashtags
- 2–4 evergreen political/global hashtags
- 3–5 context hashtags (India, leaders, regions)

DO NOT use generic tags like:
#news #update #breaking #viral

CATEGORY: {category}

TITLE:
{title}

SUMMARY:
{summary}

OUTPUT (STRICT JSON ONLY):
{{
  "headline": "...",
  "body": "...",
  "hashtags": ["#TagOne", "#TagTwo"]
}}
"""

    try:
        response = MODEL.generate_content(prompt)
        text = response.text.strip()

        # Extract JSON safely
        start = text.find("{")
        end = text.rfind("}") + 1
        data = json.loads(text[start:end])

        return {
            "headline": data.get("headline", title),
            "body": data.get("body", summary),
            "hashtags": data.get("hashtags", [])
        }

    except Exception:
        # Safe fallback
        return {
            "headline": title,
            "body": summary,
            "hashtags": []
        }

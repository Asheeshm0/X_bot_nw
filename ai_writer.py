import os
import google.generativeai as genai

# ---------------- CONFIG ----------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ---------------- MAIN FUNCTION ----------------
def rewrite_news(title: str, summary: str) -> dict:
    """
    Returns:
    {
        headline: str,
        summary: str
    }
    """

    # Fallback (always safe)
    fallback = {
        "headline": title.strip(),
        "summary": (summary or "").strip()
    }

    if not GEMINI_API_KEY:
        return fallback

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
Rewrite the following news into:
1) A short, professional headline (max 12 words)
2) A clear 1–2 sentence summary
No emojis. No hashtags. Neutral news tone.

TITLE:
{title}

SUMMARY:
{summary}
"""

        resp = model.generate_content(prompt)
        text = resp.text.strip()

        lines = [l.strip() for l in text.split("\n") if l.strip()]

        headline = lines[0] if lines else title
        clean_summary = " ".join(lines[1:3]) if len(lines) > 1 else summary

        return {
            "headline": headline[:120],
            "summary": clean_summary[:300]
        }

    except Exception:
        return fallback

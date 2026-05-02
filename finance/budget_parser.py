import os
import json
import re
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# ------------------------
# REGEX FALLBACK PARSER
# ------------------------
def fallback_parse_budgets(text: str):
    """
    Handles:
    Set food budget to 3000, travel 2000, medical 4000
    """

    text = text.lower()

    # capture: category + amount
    pattern = r"([a-zA-Z ]+)\s*(?:budget\s*(?:to)?\s*)?(\d+)"
    matches = re.findall(pattern, text)

    budgets = []

    for category, amount in matches:
        category = category.strip()

        # clean filler words
        category = re.sub(r"(set|my|budget|to|and|,)", "", category).strip()

        if category:
            budgets.append({
                "category": category,
                "monthly_limit": float(amount)
            })

    return budgets


# ------------------------
# GEMINI + FALLBACK
# ------------------------
def parse_budgets(text: str):

    try:
        prompt = f"""
Extract ALL budgets and return ONLY JSON.

Format:
[
  {{"category": "string", "monthly_limit": number}}
]

Text:
{text}
"""

        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt
        )

        raw = response.text.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]

        return json.loads(raw)

    except Exception:
        # When Gemini fails/quota exceeded
        return fallback_parse_budgets(text)

import os
import json
import re
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# ------------------------
# REGEX FALLBACK PARSER
# ------------------------
def fallback_parse_expenses(text: str):
    """
    Parses patterns like:
    1000 on food, 500 recharge, 2000 on clothes
    """

    text = text.lower()

    pattern = r"(\d+)\s*(?:on\s*)?([a-zA-Z ]+)"
    matches = re.findall(pattern, text)

    expenses = []

    for amount, category in matches:
        category = category.strip()

        # remove trailing commas or words
        category = re.sub(r"(and|,)$", "", category).strip()

        expenses.append({
            "category": category,
            "amount": float(amount)
        })

    return expenses


# ------------------------
# GEMINI + FALLBACK PARSER
# ------------------------
def parse_expenses(text: str):

    try:
        prompt = f"""
Extract ALL expenses and return ONLY JSON.

Format:
[
  {{"category": "string", "amount": number}}
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
        # When Gemini fails or quota exceeded
        return fallback_parse_expenses(text)

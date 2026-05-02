import os
import json
import re
from google import genai

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# ----------------------
# RULE-BASED FALLBACK (FAST + FREE)
# ----------------------
def fallback_intent(text: str):
    t = text.lower()

    # Expense entry
    if re.search(r"\d", t) and any(w in t for w in ["spent", "spend", "paid", "expense", "bought"]):
        return "expense_entry"

    # Budget setting
    if "budget" in t or "limit" in t:
        return "budget_setting"

    # Category query
    if any(w in t for w in ["how much", "spent on", "expense for"]):
        return "category_query"

    # Max query
    if any(w in t for w in ["highest", "most", "maximum"]):
        return "max_query"

    # Min query
    if any(w in t for w in ["lowest", "least", "minimum"]):
        return "min_query"

    # General finance summary
    finance_words = [
        "expense", "spend", "money", "cost", "total",
        "food", "shopping", "travel", "bill"
    ]
    if any(w in t for w in finance_words):
        return "summary"

    # Irrelevant query
    return "irrelevant"


# ----------------------
# AI + FALLBACK HYBRID
# ----------------------
def classify_intent(text: str):
    """
    Hybrid intent detection:
    1. Try Gemini (accurate)
    2. Fallback to rule-based (fast, reliable)
    """

    try:
        prompt = f"""
Classify user intent into ONE of:

- expense_entry
- budget_setting
- category_query
- max_query
- min_query
- summary
- irrelevant

Rules:
- Expense entry = user adding expense with amount
- Budget setting = user setting limits
- Category query = asking about specific category
- Max/min = highest or lowest spending
- Summary = general spending overview
- Irrelevant = non-finance questions

Return ONLY JSON:

{{ "intent": "one_of_above" }}

Text:
{text}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw = response.text.strip()

        # Clean markdown if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]

        intent = json.loads(raw)["intent"]

        # Safety check (VERY IMPORTANT)
        allowed = {
            "expense_entry",
            "budget_setting",
            "category_query",
            "max_query",
            "min_query",
            "summary",
            "irrelevant"
        }

        if intent not in allowed:
            return fallback_intent(text)

        return intent

    except Exception as e:
        # If Gemini fails (quota, network, etc.)
        print("Gemini failed, using fallback:", e)
        return fallback_intent(text)
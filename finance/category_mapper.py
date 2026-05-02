# finance/category_mapper.py

from typing import Dict

# -------------------------
# 1. BASE CATEGORY MAP
# -------------------------

CATEGORY_MAP: Dict[str, str] = {

    # FOOD
    "food": "Food",
    "dinner": "Food",
    "lunch": "Food",
    "breakfast": "Food",
    "pizza": "Food",
    "burger": "Food",

    # GROCERIES
    "grocery": "Groceries",
    "vegetables": "Groceries",
    "fruits": "Groceries",
    "milk": "Groceries",

    # SHOPPING
    "shopping": "Shopping",
    "clothes": "Shopping",
    "fashion": "Shopping",
    "accessories": "Shopping",

    # TRAVEL
    "uber": "Travel",
    "ola": "Travel",
    "taxi": "Travel",
    "bus": "Travel",
    "train": "Travel",

    # BILLS
    "electricity": "Bills & Utilities",
    "water": "Bills & Utilities",
    "rent": "Bills & Utilities",
    "wifi": "Bills & Utilities",

    # ENTERTAINMENT
    "movie": "Entertainment",
    "gaming": "Entertainment",

    # HEALTH
    "medicine": "Health",
    "doctor": "Health",

    # EDUCATION
    "books": "Education",
    "pen": "Education",
    "stationery": "Education",
}

# -------------------------
# 2. RULE-BASED DETECTION
# -------------------------

def rule_based_category(text: str) -> str | None:
    text = text.lower()

    # Exact match
    if text in CATEGORY_MAP:
        return CATEGORY_MAP[text]

    # Keyword match
    for key in CATEGORY_MAP:
        if key in text:
            return CATEGORY_MAP[key]

    return None


# -------------------------
# 3. AI FALLBACK (OPTIONAL)
# -------------------------

def ai_category_fallback(text: str) -> str:
    """
    Call Gemini ONLY if rule-based fails.
    Keep categories fixed.
    """

    try:
        from google import genai

        client = genai.Client()

        prompt = f"""
Classify this expense into ONE category:
Food, Groceries, Shopping, Travel, Bills & Utilities, Entertainment, Health, Education, Others.

Text: "{text}"

Only return category name.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        result = response.text.strip()

        # safety check
        allowed = [
            "Food", "Groceries", "Shopping", "Travel",
            "Bills & Utilities", "Entertainment",
            "Health", "Education", "Others"
        ]

        return result if result in allowed else "Others"

    except Exception:
        return "Others"


# -------------------------
# 4. MAIN FUNCTION
# -------------------------

def normalize_category(text: str) -> str:
    """
    Hybrid system:
    1. Rule-based
    2. AI fallback
    """

    # Step 1: rule-based
    category = rule_based_category(text)

    if category:
        return category

    # Step 2: AI fallback
    return ai_category_fallback(text)
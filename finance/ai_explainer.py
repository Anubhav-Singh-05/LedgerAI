from finance.analytics_service import financial_summary


def explain_financial_state(state):
    user_id = state["user_id"]

    data = financial_summary(user_id)

    if not data["by_category"]:
        return "You don't have any expenses recorded yet."

    text = f"💰 Total spent: ₹{data['total_spent']}\n\n"

    text += "📊 Spending by category:\n"
    for cat, amt in data["by_category"].items():
        text += f"- {cat}: ₹{amt}\n"

    text += f"\n🏆 Highest spending category: {data['top_category']} (₹{data['top_amount']})\n"

    if data["budget_exceeded"]:
        text += "\n⚠ Budgets exceeded:\n"
        for b in data["budget_exceeded"]:
            text += f"- {b['category']}: over by ₹{b['over']}\n"
    else:
        text += "\n✅ No budgets exceeded."

    return text

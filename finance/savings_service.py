from core.database import SessionLocal
from core.models import Transaction, Budget
from sqlalchemy import func


def generate_savings_suggestions(user_id):

    db = SessionLocal()

    # ------------------------
    # Spending by category
    # ------------------------
    rows = db.query(
        Transaction.category,
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense"
    ).group_by(Transaction.category).all()

    spending = {cat: float(amount) for cat, amount in rows}

    if not spending:
        db.close()
        return []

    total_spent = sum(spending.values())

    suggestions = []

    # ------------------------
    # 1. Budget overspend logic
    # ------------------------
    budgets = db.query(Budget).filter(
        Budget.user_id == user_id
    ).all()

    budget_map = {b.category: b.monthly_limit for b in budgets}

    for category, spent in spending.items():
        limit = budget_map.get(category)

        if limit and spent > limit:
            overspend = spent - limit
            save_target = round(overspend * 0.6, 2)

            suggestions.append(
                f"Reduce {category} spending by about ₹{save_target} to stay within budget."
            )

    # ------------------------
    # 2. High percentage logic
    # ------------------------
    for category, spent in spending.items():
        percent = (spent / total_spent) * 100

        if percent > 40:
            save_target = round(spent * 0.15, 2)

            suggestions.append(
                f"{category.capitalize()} takes {percent:.1f}% of your expenses. Cutting 15% could save ₹{save_target}."
            )

    # ------------------------
    # 3. General optimization
    # ------------------------
    for category, spent in spending.items():
        if spent > 1000:
            save_target = round(spent * 0.1, 2)

            suggestions.append(
                f"Reducing {category} by 10% can save around ₹{save_target}."
            )

    db.close()

    # remove duplicates
    return list(set(suggestions))

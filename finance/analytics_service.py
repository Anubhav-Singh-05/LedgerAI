from core.database import SessionLocal
from core.models import Transaction, Budget
from sqlalchemy import func


def financial_summary(user_id):
    db = SessionLocal()

    # -------------------------
    # Total spent
    # -------------------------
    total_spent = db.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense"
    ).scalar() or 0


    # -------------------------
    # By category
    # -------------------------
    rows = db.query(
        Transaction.category,
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense"
    ).group_by(Transaction.category).all()

    by_category = {cat: float(amount) for cat, amount in rows}


    # -------------------------
    # Highest & Lowest
    # -------------------------
    top_category = None
    top_amount = None
    min_category = None
    min_amount = None

    if by_category:
        top_category = max(by_category, key=by_category.get)
        top_amount = by_category[top_category]

        min_category = min(by_category, key=by_category.get)
        min_amount = by_category[min_category]


    # -------------------------
    # Budget exceeded
    # -------------------------
    budget_exceeded = []

    budgets = db.query(Budget).filter(
        Budget.user_id == user_id
    ).all()

    for b in budgets:
        spent = by_category.get(b.category, 0)

        if spent > b.monthly_limit:
            budget_exceeded.append({
                "category": b.category,
                "over": spent - b.monthly_limit
            })

    db.close()

    return {
        "total_spent": total_spent,
        "by_category": by_category,
        "top_category": top_category,
        "top_amount": top_amount,
        "min_category": min_category,
        "min_amount": min_amount,
        "budget_exceeded": budget_exceeded
    }

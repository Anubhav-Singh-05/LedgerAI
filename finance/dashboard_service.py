from core.database import SessionLocal
from core.models import Transaction, Budget
from sqlalchemy import func


def get_spending_by_category(user_id):
    db = SessionLocal()

    rows = db.query(
        Transaction.category,
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense"
    ).group_by(Transaction.category).all()

    db.close()

    return {cat: float(amount) for cat, amount in rows}


def get_spending_over_time(user_id):
    db = SessionLocal()

    rows = db.query(
        Transaction.date,
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense"
    ).group_by(Transaction.date).order_by(Transaction.date).all()

    db.close()

    return [(d, float(a)) for d, a in rows]


def get_budget_vs_actual(user_id):
    db = SessionLocal()

    budgets = db.query(Budget).filter(
        Budget.user_id == user_id
    ).all()

    actual_rows = db.query(
        Transaction.category,
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense"
    ).group_by(Transaction.category).all()

    actual_map = {c: float(a) for c, a in actual_rows}

    result = []

    for b in budgets:
        result.append({
            "category": b.category,
            "budget": b.monthly_limit,
            "actual": actual_map.get(b.category, 0)
        })

    db.close()

    return result

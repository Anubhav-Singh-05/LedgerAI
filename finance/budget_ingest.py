from core.database import SessionLocal
from core.models import Budget
from finance.budget_parser import parse_budgets


def save_budget(user_id, category, limit_amount):
    db = SessionLocal()

    existing = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.category == category
    ).first()

    if existing:
        existing.monthly_limit = limit_amount
    else:
        new_budget = Budget(
            user_id=user_id,
            category=category,
            monthly_limit=limit_amount
        )
        db.add(new_budget)

    db.commit()
    db.close()


def ingest_budgets(user_id, message):
    budgets = parse_budgets(message)

    for b in budgets:
        save_budget(
            user_id=user_id,
            category=b["category"],
            limit_amount=float(b["monthly_limit"])
        )

    return budgets


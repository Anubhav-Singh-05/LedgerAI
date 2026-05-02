from core.database import SessionLocal
from core.models import Budget


def set_budget(user_id, category, limit):
    db = SessionLocal()

    budget = Budget(
        user_id=user_id,
        category=category,
        monthly_limit=limit
    )

    db.add(budget)
    db.commit()
    db.close()

    print("Budget set:", category, limit)


if __name__ == "__main__":
    set_budget(1, "Food", 800)
    set_budget(1, "Entertainment", 2500)

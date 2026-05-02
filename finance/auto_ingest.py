from core.database import SessionLocal
from core.models import User, Transaction
from datetime import date

from finance.expense_parser import parse_expenses
from finance.category_mapper import normalize_category


# def get_or_create_user(username):
#     db = SessionLocal()

#     user = db.query(User).filter(User.name == username).first()

#     if not user:
#         user = User(name=username)
#         db.add(user)
#         db.commit()
#         db.refresh(user)

#     db.close()
#     return user.id


def save_expenses(user_id, expenses):
    db = SessionLocal()

    for e in expenses:
        tx = Transaction(
            user_id=user_id,
            date=date.today(),
            amount=float(e["amount"]),
            category=normalize_category(e["category"]),
            description="Added via chat",
            type="expense"
        )
        db.add(tx)

    db.commit()
    db.close()


def ingest_expenses(user_id, message):
    expenses = parse_expenses(message)
    save_expenses(user_id, expenses)
    return user_id, expenses

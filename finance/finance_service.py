from datetime import date
from core.database import SessionLocal
from core.models import Transaction


def add_transaction(user_id, amount, category, description="", trans_type="expense"):
    db = SessionLocal()

    tx = Transaction(
        user_id=user_id,
        date=date.today(),
        amount=amount,
        category=category,
        description=description,
        type=trans_type
    )

    db.add(tx)
    db.commit()
    db.close()

    print("Added:", amount, category)


if __name__ == "__main__":
    add_transaction(1, 1000, "Food", "Lunch")
    add_transaction(1, 3000, "Entertainment", "Movie night")
    add_transaction(1, 50000, "Medical", "Hospital bill")
    add_transaction(1, 4000, "Education", "Online course")

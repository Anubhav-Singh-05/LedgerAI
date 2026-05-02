import pandas as pd
from core.database import SessionLocal
from core.models import Transaction
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
from sqlalchemy import func


def fetch_monthly_expenses(user_id):
    db = SessionLocal()

    results = (
        db.query(
            func.extract("year", Transaction.date).label("year"),
            func.extract("month", Transaction.date).label("month"),
            func.sum(Transaction.amount).label("total")
        )
        .filter(Transaction.user_id == user_id)
        .filter(Transaction.type == "expense")
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )

    db.close()

    data = []
    for i, r in enumerate(results):
        data.append([i, float(r.total)])

    return pd.DataFrame(data, columns=["time_index", "total_expense"])


def train_and_predict(user_id):
    df = fetch_monthly_expenses(user_id)

    if len(df) < 2:
        print("Not enough data for prediction yet.")
        return

    X = df[["time_index"]]
    y = df["total_expense"]

    model = LinearRegression()
    model.fit(X, y)

    next_index = [[len(df)]]
    prediction = model.predict(next_index)

    print("Predicted next month expense:", round(prediction[0], 2))


if __name__ == "__main__":
    train_and_predict(1)

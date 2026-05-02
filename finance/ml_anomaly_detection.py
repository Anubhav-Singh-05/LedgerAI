import pandas as pd
from core.database import SessionLocal
from core.models import Transaction
from sklearn.ensemble import IsolationForest


def detect_anomalies(user_id):
    db = SessionLocal()

    txs = (
        db.query(Transaction.amount)
        .filter(Transaction.user_id == user_id)
        .filter(Transaction.type == "expense")
        .all()
    )

    db.close()

    amounts = [float(t.amount) for t in txs]

    if len(amounts) < 5:
        print("Not enough data for anomaly detection.")
        return

    df = pd.DataFrame(amounts, columns=["amount"])

    model = IsolationForest(contamination=0.2, random_state=42)
    df["anomaly"] = model.fit_predict(df)

    anomalies = df[df["anomaly"] == -1]

    print("Unusual expenses detected:")
    print(anomalies)


if __name__ == "__main__":
    detect_anomalies(1)

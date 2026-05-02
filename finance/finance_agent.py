from finance.analytics_service import (
    total_spent_by_category,
    biggest_expense,
    monthly_total,
    check_budget
)

from finance.ml_expense_prediction import train_and_predict
from finance.ml_anomaly_detection import detect_anomalies
from finance.notification_service import send_budget_alerts
from datetime import date


class FinanceAgent:

    def financial_summary(self, user_id):
        today = date.today()

        totals = total_spent_by_category(user_id)
        biggest = biggest_expense(user_id)
        month_total = monthly_total(user_id, today.year, today.month)
        alerts = check_budget(user_id)

        summary = {
            "monthly_total": month_total,
            "biggest_expense": {
                "category": biggest.category,
                "amount": biggest.amount
            },
            "category_totals": totals,
            "budget_alerts": alerts
        }

        return summary


    def run_predictions(self, user_id):
        print("\n🔮 Running expense prediction:")
        train_and_predict(user_id)

        print("\n🚨 Running anomaly detection:")
        detect_anomalies(user_id)


    def full_autonomous_check(self, user_id):
        print("\n📊 Generating financial summary...")
        summary = self.financial_summary(user_id)

        print(summary)

        print("\n🔔 Checking budget alerts...")
        send_budget_alerts(user_id)

        print("\n🤖 Running AI predictions...")
        self.run_predictions(user_id)


if __name__ == "__main__":
    agent = FinanceAgent()
    agent.full_autonomous_check(1)

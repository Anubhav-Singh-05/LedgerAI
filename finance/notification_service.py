from finance.analytics_service import check_budget


def send_budget_alerts(user_id):
    alerts = check_budget(user_id)

    if not alerts:
        print("No budget alerts. All good 👍")
        return

    for alert in alerts:
        print(
            f"⚠ ALERT: You exceeded your {alert['category']} budget!\n"
            f"Spent: {alert['spent']} | Limit: {alert['limit']}\n"
        )


if __name__ == "__main__":
    send_budget_alerts(1)

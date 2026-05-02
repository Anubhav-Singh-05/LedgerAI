import streamlit as st
import pandas as pd

from core.auth import signup_user, login_user

from finance.intent_classifier import classify_intent
from finance.auto_ingest import ingest_expenses
from finance.budget_ingest import ingest_budgets
from finance.analytics_service import financial_summary
# from finance.savings import generate_savings_suggestions

def is_finance_query(text: str) -> bool:
    text = text.lower()

    keywords = [
        "spend", "spent", "expense", "expenses",
        "budget", "money", "cost", "price",
        "how much", "total", "highest", "lowest",
        "food", "shopping", "travel", "bill"
    ]

    return any(k in text for k in keywords)

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="AI Finance Assistant", layout="centered")
st.title("💰 AI Personal Finance Assistant")


# ----------------------------
# Session state
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_id" not in st.session_state:
    st.session_state.user_id = None


# ----------------------------
# 🔐 AUTH SYSTEM
# ----------------------------
if st.session_state.user_id is None:

    st.subheader("🔐 Login / Signup")

    option = st.radio("Choose", ["Login", "Signup"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Submit"):

        if option == "Signup":
            user, error = signup_user(email, password)

            if error:
                st.error(error)
            else:
                st.success("Account created! Please login.")

        else:
            user, error = login_user(email, password)

            if error:
                st.error(error)
            else:
                st.session_state.user_id = user.id
                st.success("Logged in successfully!")
                st.rerun()

    st.stop()


# ----------------------------
# ✅ Logged-in UI
# ----------------------------
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(f"👤 Logged in (User ID: {st.session_state.user_id})")

with col2:
    if st.button("Logout"):
        st.session_state.user_id = None
        st.session_state.messages = []
        st.rerun()


# ----------------------------
# Show chat history
# ----------------------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])


# ----------------------------
# Chat input
# ----------------------------
user_input = st.chat_input("Add expenses, set budgets, or ask questions...")


if user_input:

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # ============================
    # INTENT ROUTING
    # ============================
    intent = classify_intent(user_input)

    # ---------------- EXPENSE ENTRY ----------------
    if intent == "expense_entry":

        try:
            _, expenses = ingest_expenses(
                st.session_state.user_id,
                user_input
            )

            response = f"✅ Saved {len(expenses)} expenses successfully!"

        except Exception as e:
            response = f"❌ Failed to save expenses: {e}"

    # ---------------- BUDGET SETTING ----------------
    elif intent == "budget_setting":

        try:
            budgets = ingest_budgets(
                st.session_state.user_id,
                user_input
            )

            summary = ", ".join(
                f"{b['category']} (₹{b['monthly_limit']})"
                for b in budgets
            )

            response = f"📌 Budgets updated: {summary}"

        except Exception as e:
            response = f"❌ Failed to set budgets: {e}"

    # ---------------- ANALYSIS ----------------
    else:

        # ❌ Handle irrelevant queries first
        if not is_finance_query(user_input):
            response = "⚠ Please ask questions related to your expenses, budgets, or spending."

        else:
            data = financial_summary(st.session_state.user_id)

            if not data["by_category"]:
                response = "You don't have any expenses yet."

            else:
                question = user_input.lower()

                matched = False

                # -------- CATEGORY QUERY --------
                for cat in data["by_category"]:
                    if cat.lower() in question:
                        response = f"💰 You have spent ₹{data['by_category'][cat]} on {cat}."
                        matched = True
                        break

                # -------- MIN --------
                if not matched and ("minimum" in question or "least" in question or "lowest" in question):
                    response = f"📉 Lowest spending: {data['min_category']} (₹{data['min_amount']})"

                # -------- MAX --------
                elif not matched and ("maximum" in question or "most" in question or "highest" in question):
                    response = f"🏆 Highest spending: {data['top_category']} (₹{data['top_amount']})"

                # -------- DEFAULT --------
                elif not matched:
                    response = f"""
    💰 Total spent: ₹{data['total_spent']}

    📊 By category:
    {chr(10).join(f"- {k}: ₹{v}" for k,v in data['by_category'].items())}

    🏆 Highest: {data['top_category']} (₹{data['top_amount']})
📉 Lowest: {data['min_category']} (₹{data['min_amount']})
    """


                if data["budget_exceeded"]:
                    response += "\n⚠ Budgets exceeded:\n"
                    for b in data["budget_exceeded"]:
                        response += f"- {b['category']} over by ₹{b['over']}\n"
                else:
                    response += "\n✅ No budgets exceeded."

        # # SAVINGS
        # suggestions = generate_savings_suggestions(
        #     st.session_state.user_id
        # )

        # if suggestions:
        #     response += "\n\n💡 Savings Suggestions:\n"
        #     for s in suggestions[:5]:
        #         response += f"- {s}\n"

    # ----------------------------
    # Show assistant reply
    # ----------------------------
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

    with st.chat_message("assistant"):
        st.markdown(response)



from core.database import SessionLocal
from core.models import Transaction, Budget
from sqlalchemy import func


def get_spending_by_category(user_id):
    db = SessionLocal()

    results = (
        db.query(
            Transaction.category,
            func.sum(Transaction.amount)
        )
        .filter(Transaction.user_id == user_id)
        .group_by(Transaction.category)
        .all()
    )

    db.close()

    return {r[0]: r[1] for r in results}


def get_spending_over_time(user_id):
    db = SessionLocal()

    results = (
        db.query(
            Transaction.date,
            func.sum(Transaction.amount)
        )
        .filter(Transaction.user_id == user_id)
        .group_by(Transaction.date)
        .order_by(Transaction.date)
        .all()
    )

    db.close()

    return [(r[0], r[1]) for r in results]


def get_budget_vs_actual(user_id):
    db = SessionLocal()

    results = (
        db.query(
            Budget.category,
            Budget.monthly_limit,
            func.sum(Transaction.amount)
        )
        .join(Transaction, Transaction.category == Budget.category)
        .filter(Budget.user_id == user_id)
        .group_by(Budget.category, Budget.monthly_limit)
        .all()
    )

    db.close()

    return [
        {
            "category": r[0],
            "budget": r[1],
            "actual": r[2] or 0
        }
        for r in results
    ]

# ============================
# 📊 DASHBOARD
# ============================

st.divider()
st.header("📊 Spending Dashboard")

# Category chart
category_data = get_spending_by_category(st.session_state.user_id)

if category_data:
    st.subheader("Spending by Category")
    st.bar_chart(category_data)

# Time chart
time_data = get_spending_over_time(st.session_state.user_id)

if len(time_data) > 1:
    df_time = pd.DataFrame(time_data, columns=["date", "amount"])
    df_time["date"] = pd.to_datetime(df_time["date"])
    df_time = df_time.set_index("date")

    st.subheader("Spending Over Time")
    st.line_chart(df_time)

elif len(time_data) == 1:
    st.info("Add expenses on multiple days to see spending trend 📈")

# Budget chart
budget_data = get_budget_vs_actual(st.session_state.user_id)

if budget_data:
    st.subheader("Budget vs Actual")

    chart_data = {
        row["category"]: {
            "Budget": row["budget"],
            "Actual": row["actual"]
        }
        for row in budget_data
    }

    st.bar_chart(chart_data)
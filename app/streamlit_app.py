import streamlit as st

from bank_analytics.analytics import analytics
from bank_analytics.config.configuration import ConfigurationManager
from bank_analytics.database.bank import Bank

# ================= CONFIG ==================
config_manager = ConfigurationManager()
db_config = config_manager.get_database_config()
app_config = config_manager.get_app_config()
# ============================================


# ================= SESSION ==================
if "accno" not in st.session_state:
    st.session_state.accno = 0

if "pin" not in st.session_state:
    st.session_state.pin = ""
# ============================================


# ================= BANK OBJECT ==============
bank = Bank(db_config)
# ============================================


st.markdown(
    f"<h1 style='text-align:center;'>🏦 {app_config.page_title}</h1>",
    unsafe_allow_html=True,
)

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Create Account",
        "Deposit",
        "Withdraw",
        "Check Balance",
        "Transaction History",
        "Data Analysis",
        "Delete Account",
    ],
)

# ================= CREATE ACCOUNT =================
if menu == "Create Account":
    st.subheader("Create New Account")

    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0)

    email = st.text_input("Email")
    pin = st.text_input("PIN (4 digits)", type="password")

    if st.button("Create Account"):
        success, result = bank.create_account(name, age, email, int(pin))
        if success:
            st.success("Account Created Successfully 🎉")
            st.write(result)
        else:
            st.error(result)


# ================= DEPOSIT =================
elif menu == "Deposit":
    st.subheader("Deposit Money")

    acc = st.number_input("Account Number", value=st.session_state.accno, step=1)
    pin = st.text_input("PIN", type="password", value=st.session_state.pin)
    amt = st.number_input("Amount", min_value=1)

    if st.button("Deposit"):
        success, msg = bank.deposit(acc, int(pin), amt)
        if success:
            st.success(f"New Balance: ₹{msg}")
            st.session_state.accno = acc
            st.session_state.pin = pin
        else:
            st.error(msg)


# ================= WITHDRAW =================
elif menu == "Withdraw":
    st.subheader("Withdraw Money")

    acc = st.number_input("Account Number", value=st.session_state.accno, step=1)
    pin = st.text_input("PIN", type="password", value=st.session_state.pin)
    amt = st.number_input("Amount", min_value=1)

    if st.button("Withdraw"):
        success, msg = bank.withdraw(acc, int(pin), amt)
        if success:
            st.success(f"Remaining Balance: ₹{msg}")
        else:
            st.error(msg)


# ================= CHECK BALANCE =================
elif menu == "Check Balance":
    st.subheader("Check Account Balance")

    acc = st.number_input("Account Number", value=st.session_state.accno, step=1)
    pin = st.text_input("PIN", type="password", value=st.session_state.pin)

    if st.button("Check Balance"):
        success, bal = bank.check_balance(acc, int(pin))
        if success:
            st.success(f"Available Balance: ₹{bal}")
        else:
            st.error(bal)


# ================= TRANSACTION HISTORY =================
elif menu == "Transaction History":
    st.subheader("Transaction History")

    acc = st.number_input("Account Number", value=st.session_state.accno, step=1)
    pin = st.text_input("PIN", type="password", value=st.session_state.pin)

    if st.button("View History"):
        rows = bank.get_transactions(acc, int(pin))
        if rows:
            st.table(rows)
        else:
            st.error("Invalid account or no transactions found")


# ================= DATA ANALYSIS =================
elif menu == "Data Analysis":
    st.subheader("📊 Banking Data Analysis (Real-World Dashboard)")

    df = analytics.clean_df(analytics.load_df(bank.conn))

    if df.empty:
        st.warning("No transaction data available")
    else:
        # ---------- KPI SECTION ----------
        kpis = analytics.business_kpis(df)

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Txns", kpis["total_transactions"])
        col2.metric("Inflow", f"₹{kpis['total_inflow']:.2f}")
        col3.metric("Outflow", f"₹{kpis['total_outflow']:.2f}")
        col4.metric("Net Flow", f"₹{kpis['net_cash_flow']:.2f}")
        col5.metric("Avg Txn", f"₹{kpis['avg_transaction_value']:.2f}")

        st.divider()

        # ---------- DAILY TREND ----------
        st.subheader("📈 Daily Transaction Trend")
        st.pyplot(analytics.daily_transaction_volume(df))

        st.divider()

        # ---------- ACCOUNT SUMMARY ----------
        st.subheader("🏦 Account Summary (Real Insight)")
        acc_summary = analytics.account_summary(df)
        st.dataframe(acc_summary)
        st.bar_chart(acc_summary.set_index("accountno")["total_balance"])

        st.divider()

        # ---------- TOP ACCOUNTS ----------
        st.subheader("🔥 Top Active Accounts")
        st.dataframe(analytics.top_active_accounts(df, app_config))

        st.divider()

        # ---------- AGE GROUP ----------
        st.subheader("👥 Age Group Analysis")
        age_data = analytics.age_group_analysis(df, app_config)

        if age_data is not None:
            st.dataframe(age_data)
            st.bar_chart(age_data.set_index("age_group"))
        else:
            st.info("No age data available")

        st.divider()

        # ---------- RISK SECTION ----------
        st.subheader("🚨 Risk Monitoring")

        high_risk = analytics.high_value_transactions(df, app_config)
        st.write("High Value Transactions")
        st.dataframe(high_risk)

        risk_df = analytics.risk_scoring(df, app_config)
        st.write("Risk Scoring")
        st.dataframe(risk_df[["accountno", "amount", "risk_score"]])

        st.divider()

        # ---------- DISTRIBUTION ----------
        st.subheader("📦 Cash Flow Distribution")
        st.pyplot(analytics.cash_flow_distribution(df))

        st.divider()

        # ---------- BUSINESS INSIGHTS ----------
        st.subheader("🧠 Key Business Insights")

        biz_insights = analytics.insights(df)

        col1, col2, col3 = st.columns(3)
        col1.success(
            f"💰 Highest Txn\n\n₹{biz_insights['highest_transaction']} (Acc {biz_insights['highest_account']})"
        )
        col2.warning(
            f"📉 Lowest Txn\n\n₹{biz_insights['lowest_transaction']} (Acc {biz_insights['lowest_account']})"
        )
        col3.info(f"🏦 Total Deposits\n\n₹{biz_insights['total_deposits']}")


# ================= DELETE ACCOUNT =================
elif menu == "Delete Account":
    st.subheader("Delete Account")

    acc = st.number_input("Account Number", value=st.session_state.accno, step=1)
    pin = st.text_input("PIN", type="password", value=st.session_state.pin)

    if st.button("Delete Account"):
        success, msg = bank.delete_account(acc, int(pin))
        if success:
            st.success(msg)
            st.session_state.accno = 0
            st.session_state.pin = ""
        else:
            st.error(msg)

import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from bank_analytics.entity.config_entity import AppConfig
from bank_analytics.exception import BankAnalyticsException
from bank_analytics.utils.logger import logger


def load_df(conn) -> pd.DataFrame:
    try:
        return pd.read_sql("SELECT * FROM transactions", conn)
    except Exception as e:
        raise BankAnalyticsException(e, sys) from e


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    try:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y %H:%M", errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        if "age" in df.columns:
            df["age"] = pd.to_numeric(df["age"], errors="coerce")
        df.dropna(inplace=True)
        return df
    except Exception as e:
        raise BankAnalyticsException(e, sys) from e


def business_kpis(df: pd.DataFrame) -> dict:
    total_inflow = df[df["type"] == "Deposit"]["amount"].sum()
    total_outflow = df[df["type"] == "Withdraw"]["amount"].sum()
    return {
        "total_transactions": len(df),
        "total_inflow": total_inflow,
        "total_outflow": total_outflow,
        "net_cash_flow": total_inflow - total_outflow,
        "avg_transaction_value": df["amount"].mean(),
    }


def account_summary(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("accountno").agg(
        total_balance=("amount", "sum"),
        total_transactions=("amount", "count"),
        avg_transaction=("amount", "mean"),
    ).reset_index()


def daily_transaction_volume(df: pd.DataFrame):
    daily = df.groupby(df["date"].dt.date)["amount"].sum()
    plt.figure(figsize=(7, 4))
    daily.plot()
    plt.title("Daily Transaction Volume")
    plt.xlabel("Date")
    plt.ylabel("Total Amount")
    plt.tight_layout()
    return plt


def top_active_accounts(df: pd.DataFrame, app_config: AppConfig) -> pd.DataFrame:
    return (
        df.groupby("accountno")
        .size()
        .sort_values(ascending=False)
        .head(app_config.top_active_accounts_n)
        .reset_index(name="transaction_count")
    )


def high_value_transactions(df: pd.DataFrame, app_config: AppConfig) -> pd.DataFrame:
    threshold = df["amount"].mean() + app_config.high_value_std_multiplier * df["amount"].std()
    flagged = df[df["amount"] > threshold].copy()
    flagged["risk_flag"] = "High Value Transaction"
    return flagged


def cash_flow_distribution(df: pd.DataFrame):
    plt.figure(figsize=(6, 4))
    sns.boxplot(x="type", y="amount", data=df)
    plt.title("Cash Flow Distribution")
    plt.tight_layout()
    return plt


def running_balance(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("date")
    df["running_balance"] = df["amount"].cumsum()
    return df


def age_group_analysis(df: pd.DataFrame, app_config: AppConfig):
    if "age" not in df.columns:
        return None
    df = df.copy()
    df["age_group"] = pd.cut(df["age"], bins=app_config.age_bins, labels=app_config.age_labels)
    return df.groupby("age_group")["amount"].mean().reset_index()


def risk_scoring(df: pd.DataFrame, app_config: AppConfig) -> pd.DataFrame:
    df = df.copy()
    df["hour"] = df["date"].dt.hour
    df["risk_score"] = np.where(
        (df["amount"] > df["amount"].quantile(app_config.risk_high_quantile))
        & (df["hour"] < app_config.risk_night_hour_cutoff),
        "High",
        np.where(
            df["amount"] > df["amount"].quantile(app_config.risk_medium_quantile),
            "Medium",
            "Low",
        ),
    )
    return df


def insights(df: pd.DataFrame) -> dict:
    highest_txn = df.loc[df["amount"].idxmax()]
    lowest_txn = df.loc[df["amount"].idxmin()]
    total_deposits = df[df["type"] == "Deposit"]["amount"].sum()
    return {
        "highest_transaction": highest_txn["amount"],
        "highest_account": highest_txn["accountno"],
        "lowest_transaction": lowest_txn["amount"],
        "lowest_account": lowest_txn["accountno"],
        "total_deposits": total_deposits,
    }

import pandas as pd

from bank_analytics.analytics import analytics


def _sample_df():
    return pd.DataFrame(
        {
            "accountno": [1, 1, 2, 2],
            "type": ["Deposit", "Withdraw", "Deposit", "Deposit"],
            "amount": [1000, 200, 500, 1500],
            "date": [
                "01-01-2026 10:00",
                "02-01-2026 11:00",
                "01-01-2026 09:00",
                "03-01-2026 23:00",
            ],
            "balance": [1000, 800, 500, 2000],
        }
    )


def test_clean_df_parses_types():
    df = analytics.clean_df(_sample_df())
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert pd.api.types.is_numeric_dtype(df["amount"])


def test_business_kpis_totals():
    df = analytics.clean_df(_sample_df())
    kpis = analytics.business_kpis(df)
    assert kpis["total_transactions"] == 4
    assert kpis["total_inflow"] == 3000
    assert kpis["total_outflow"] == 200
    assert kpis["net_cash_flow"] == 2800

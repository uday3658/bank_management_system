from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    user: str
    password: str
    database: str
    port: int


@dataclass(frozen=True)
class AppConfig:
    page_title: str
    high_value_std_multiplier: float
    risk_high_quantile: float
    risk_medium_quantile: float
    risk_night_hour_cutoff: int
    top_active_accounts_n: int
    age_bins: List[int]
    age_labels: List[str]

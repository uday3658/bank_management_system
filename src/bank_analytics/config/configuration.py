import os
import sys

from dotenv import load_dotenv

from bank_analytics.constants import CONFIG_FILE_PATH
from bank_analytics.entity.config_entity import AppConfig, DatabaseConfig
from bank_analytics.exception import BankAnalyticsException
from bank_analytics.utils.common import read_yaml
from bank_analytics.utils.logger import logger

load_dotenv()


class ConfigurationManager:
    """Single source of truth for config — reads config.yaml for structure/
    tunables and .env for secrets, then dispenses typed config dataclasses."""

    def __init__(self, config_filepath=CONFIG_FILE_PATH):
        self.config = read_yaml(config_filepath)

    def get_database_config(self) -> DatabaseConfig:
        try:
            db = self.config["database"]
            password = os.getenv("DB_PASSWORD")
            if password is None:
                logger.warning(
                    "DB_PASSWORD not set in environment — falling back to empty string. "
                    "Create a .env file from .env.example."
                )
            return DatabaseConfig(
                host=db["host"],
                user=db["user"],
                password=password or "",
                database=db["database"],
                port=db["port"],
            )
        except Exception as e:
            raise BankAnalyticsException(e, sys) from e

    def get_app_config(self) -> AppConfig:
        try:
            app = self.config["app"]
            return AppConfig(**app)
        except Exception as e:
            raise BankAnalyticsException(e, sys) from e

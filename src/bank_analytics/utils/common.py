from pathlib import Path

import yaml

from bank_analytics.exception import BankAnalyticsException
from bank_analytics.utils.logger import logger
import sys


def read_yaml(path: Path) -> dict:
    """Read a YAML file and return its contents as a dict."""
    try:
        with open(path, "r") as f:
            content = yaml.safe_load(f)
        logger.info(f"YAML file loaded successfully from: {path}")
        return content
    except Exception as e:
        raise BankAnalyticsException(e, sys) from e

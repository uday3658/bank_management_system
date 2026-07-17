import random
import sys
from datetime import datetime

import mysql.connector

from bank_analytics.entity.config_entity import DatabaseConfig
from bank_analytics.exception import BankAnalyticsException
from bank_analytics.utils.logger import logger


class Bank:
    """Handles account + transaction operations against MySQL.
    Takes a DatabaseConfig instead of hardcoded credentials."""

    def __init__(self, db_config: DatabaseConfig):
        try:
            self.conn = mysql.connector.connect(
                host=db_config.host,
                user=db_config.user,
                password=db_config.password,
                database=db_config.database,
                port=db_config.port,
                autocommit=True,
            )
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to MySQL database '{db_config.database}'")
        except Exception as e:
            raise BankAnalyticsException(e, sys) from e

    def generate_account(self) -> int:
        return random.randint(10**11, 10**12 - 1)

    def find_user(self, accno, pin):
        try:
            self.cursor.execute(
                "SELECT * FROM users WHERE accountno=%s AND pin=%s",
                (accno, pin),
            )
            return self.cursor.fetchone()
        except Exception as e:
            raise BankAnalyticsException(e, sys) from e

    def create_account(self, name, age, email, pin):
        if not name or age < 18 or len(str(pin)) != 4:
            return False, "Age must be 18+ and PIN must be 4 digits"
        try:
            accno = self.generate_account()
            self.cursor.execute(
                """
                INSERT INTO users (name, age, email, pin, accountno, balance)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (name, age, email, pin, accno, 0),
            )
            logger.info(f"Account created: {accno}")
            return True, {"accountno": accno, "balance": 0}
        except Exception as e:
            raise BankAnalyticsException(e, sys) from e

    def check_balance(self, accno, pin):
        user = self.find_user(accno, pin)
        if not user:
            return False, "Invalid account or PIN"
        return True, user[6]

    def deposit(self, accno, pin, amount):
        user = self.find_user(accno, pin)
        if not user:
            return False, "Invalid account or PIN"
        try:
            new_balance = user[6] + amount
            self.cursor.execute(
                "UPDATE users SET balance=%s WHERE accountno=%s",
                (new_balance, accno),
            )
            self.cursor.execute(
                """
                INSERT INTO transactions (accountno, type, amount, date, balance)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (accno, "Deposit", amount, datetime.now().strftime("%d-%m-%Y %H:%M"), new_balance),
            )
            logger.info(f"Deposit of {amount} to account {accno}")
            return True, new_balance
        except Exception as e:
            raise BankAnalyticsException(e, sys) from e

    def withdraw(self, accno, pin, amount):
        user = self.find_user(accno, pin)
        if not user or amount > user[6]:
            return False, "Invalid or insufficient balance"
        try:
            new_balance = user[6] - amount
            self.cursor.execute(
                "UPDATE users SET balance=%s WHERE accountno=%s",
                (new_balance, accno),
            )
            self.cursor.execute(
                """
                INSERT INTO transactions (accountno, type, amount, date, balance)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (accno, "Withdraw", amount, datetime.now().strftime("%d-%m-%Y %H:%M"), new_balance),
            )
            logger.info(f"Withdrawal of {amount} from account {accno}")
            return True, new_balance
        except Exception as e:
            raise BankAnalyticsException(e, sys) from e

    def get_transactions(self, accno, pin):
        if not self.find_user(accno, pin):
            return None
        try:
            self.cursor.execute(
                "SELECT type, amount, date, balance FROM transactions WHERE accountno=%s",
                (accno,),
            )
            return self.cursor.fetchall()
        except Exception as e:
            raise BankAnalyticsException(e, sys) from e

    def delete_account(self, accno, pin):
        if not self.find_user(accno, pin):
            return False, "Invalid credentials"
        try:
            self.cursor.execute("DELETE FROM users WHERE accountno=%s", (accno,))
            self.cursor.execute("DELETE FROM transactions WHERE accountno=%s", (accno,))
            logger.info(f"Account deleted: {accno}")
            return True, "Account deleted"
        except Exception as e:
            raise BankAnalyticsException(e, sys) from e

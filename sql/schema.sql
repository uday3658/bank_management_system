-- Bank Transaction Analytics System
-- MySQL schema
-- Run once before starting the app: mysql -u root -p < sql/schema.sql

CREATE DATABASE IF NOT EXISTS bank_db;
USE bank_db;

CREATE TABLE IF NOT EXISTS users (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    age        INT NOT NULL,
    email      VARCHAR(150),
    pin        INT NOT NULL,
    accountno  BIGINT UNIQUE NOT NULL,
    balance    DECIMAL(12, 2) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS transactions (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    accountno  BIGINT NOT NULL,
    type       VARCHAR(20) NOT NULL,   -- 'Deposit' or 'Withdraw'
    amount     DECIMAL(12, 2) NOT NULL,
    date       VARCHAR(20) NOT NULL,   -- stored as '%d-%m-%Y %H:%M'
    balance    DECIMAL(12, 2) NOT NULL,
    FOREIGN KEY (accountno) REFERENCES users(accountno)
);

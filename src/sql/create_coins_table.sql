-- SQL script to create the coins table schema
-- Usage: Placeholder {table} is formatted in Python before execution
DROP TABLE IF EXISTS {table} CASCADE;

CREATE TABLE IF NOT EXISTS {table} (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    symbol TEXT NOT NULL UNIQUE,
    time_start TIMESTAMPTZ NOT NULL,
    time_buy TIMESTAMPTZ,
    time_sell TIMESTAMPTZ,
    price_buy DECIMAL(18,8),
    price_sell DECIMAL(18,8),
    fund_buy DECIMAL(18,8),
    fund_sell DECIMAL(18,8),
    profit DECIMAL(18,8)
);

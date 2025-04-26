-- SQL script to create the coins table schema
-- Usage: Placeholder {table} is formatted in Python before execution
-- This table tracks cryptocurrencies and their trading information

-- TRADING INFORMATION TRACKING:
-- This table stores basic information about cryptocurrencies and their trading history
-- It can be used to track buy/sell operations and calculate profits/losses

DROP TABLE IF EXISTS {table} CASCADE;

CREATE TABLE IF NOT EXISTS {table} (
    -- Basic identification
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,                 -- Full name of the cryptocurrency (e.g., Bitcoin)
    symbol TEXT NOT NULL UNIQUE,        -- Trading symbol (e.g., BTC)
    
    -- Timestamps for tracking
    time_start TIMESTAMPTZ NOT NULL,    -- When tracking of this coin started
    time_buy TIMESTAMPTZ,               -- When the coin was purchased
    time_sell TIMESTAMPTZ,              -- When the coin was sold
    
    -- Price information
    price_buy DECIMAL(18,8),            -- Purchase price in USD
    price_sell DECIMAL(18,8),           -- Selling price in USD
    
    -- Financial tracking
    fund_buy DECIMAL(18,8),             -- Amount spent on purchase in USD
    fund_sell DECIMAL(18,8),            -- Amount received from sale in USD
    profit DECIMAL(18,8)                -- Calculated profit/loss (fund_sell - fund_buy)
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_{table}_symbol ON {table}(symbol);

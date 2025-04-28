-- SQL script to create the coins table schema
-- Usage: Placeholder coins is formatted in Python before execution
-- This table tracks cryptocurrencies and their trading information

-- TRADING INFORMATION TRACKING:
-- This table stores basic information about cryptocurrencies and their trading history
-- It can be used to track buy/sell operations and calculate profits/losses


CREATE TABLE IF NOT EXISTS coins (
    -- Basic identification
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,                 -- Full name of the cryptocurrency (e.g., Bitcoin)
    symbol TEXT NOT NULL UNIQUE,        -- Trading symbol (e.g., BTC)
    futures BOOLEAN NOT NULL DEFAULT FALSE,   -- TRUE if coin is listed in futures, FALSE otherwise
    
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
    profit DECIMAL(18,8),               -- Calculated profit/loss (fund_sell - fund_buy)

    -- Timestamps for record creation and updates
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_coins_symbol ON coins(symbol);

-- Create trigger function to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column_coins()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger to table
CREATE TRIGGER set_updated_at_coins
BEFORE UPDATE ON coins
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column_coins();

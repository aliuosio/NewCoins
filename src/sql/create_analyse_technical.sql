-- Drop existing table and related trigger/function
DROP TABLE IF EXISTS {table} CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column_{table} CASCADE;

-- Technical indicators scoring criteria

-- Create the table
CREATE TABLE IF NOT EXISTS {table} (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    trading_volume_score DECIMAL(5,2),
    liquidity_score DECIMAL(5,2),
    whale_transactions_score DECIMAL(5,2),
    token_distribution_score DECIMAL(5,2),
    pre_sale_vesting_score DECIMAL(5,2),
    smart_contract_audit_score DECIMAL(5,2),

    analysis_date DATE NOT NULL DEFAULT CURRENT_DATE,
    recommendation TEXT,  -- Assumed from index, add if needed

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(symbol, analysis_date)
);

-- Add column comments
COMMENT ON COLUMN {table}.trading_volume_score IS '15 points - >$1M in first 24h on another exchange';
COMMENT ON COLUMN {table}.liquidity_score IS '15 points - Tight spread (<0.5%), deep order book';
COMMENT ON COLUMN {table}.whale_transactions_score IS '10 points - >50% whale buys, no mass sell-offs';
COMMENT ON COLUMN {table}.token_distribution_score IS '10 points - No single wallet holding >10%';
COMMENT ON COLUMN {table}.smart_contract_audit_score IS '10 points - Certik/SlowMist audit, no vulnerabilities';
COMMENT ON COLUMN {table}.pre_sale_vesting_score IS '10 points - No major unlocks in next 30 days';

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_{table}_symbol ON {table}(symbol);
CREATE INDEX IF NOT EXISTS idx_{table}_date ON {table}(analysis_date);
CREATE INDEX IF NOT EXISTS idx_{table}_recommendation ON {table}(recommendation);

-- Create trigger function to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column_{table}()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger to table
CREATE TRIGGER set_updated_at_{table}
BEFORE UPDATE ON {table}
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column_{table}();

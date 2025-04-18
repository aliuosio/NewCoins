-- Drop existing table and related trigger/function
DROP TABLE IF EXISTS {table} CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column_{table} CASCADE;

-- Technical indicators scoring criteria

-- Create the table
CREATE TABLE IF NOT EXISTS {table} (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    
    -- Technical indicator scores
    trading_volume_score DECIMAL(5,2),
    liquidity_score DECIMAL(5,2),
    whale_transactions_score DECIMAL(5,2),
    token_distribution_score DECIMAL(5,2),
    pre_sale_vesting_score DECIMAL(5,2),
    smart_contract_audit_score DECIMAL(5,2),
    
    -- Indicator applicability flags
    pre_sale_vesting_applicable BOOLEAN DEFAULT TRUE,
    smart_contract_audit_applicable BOOLEAN DEFAULT TRUE,


    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(symbol) -- Only one record per coin
);

-- Add column comments
COMMENT ON COLUMN {table}.trading_volume_score IS '15 points - >$1M in first 24h on another exchange';
COMMENT ON COLUMN {table}.liquidity_score IS '15 points - Tight spread (<0.5%), deep order book';
COMMENT ON COLUMN {table}.whale_transactions_score IS '10 points - >50% whale buys, no mass sell-offs';
COMMENT ON COLUMN {table}.token_distribution_score IS '10 points - No single wallet holding >10%';
COMMENT ON COLUMN {table}.smart_contract_audit_score IS '10 points - Certik/SlowMist audit, no vulnerabilities';
COMMENT ON COLUMN {table}.pre_sale_vesting_score IS '10 points - No major unlocks in next 30 days';

-- Add comments for applicability flags
COMMENT ON COLUMN {table}.pre_sale_vesting_applicable IS 'Flag indicating if pre-sale vesting indicator is applicable to this cryptocurrency';
COMMENT ON COLUMN {table}.smart_contract_audit_applicable IS 'Flag indicating if smart contract audit indicator is applicable to this cryptocurrency';

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_{table}_symbol ON {table}(symbol);

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

-- SQL script to create the crypto_analysis table schema
-- This table stores the results of cryptocurrency analysis
DROP TABLE IF EXISTS {table} CASCADE;

CREATE TABLE IF NOT EXISTS {table} (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    analysis_date TIMESTAMPTZ NOT NULL,
    
    -- Overall scores
    total_score DECIMAL(5,2) NOT NULL,
    max_score DECIMAL(5,2) NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    recommendation TEXT NOT NULL,
    
    -- Individual indicator scores
    trading_volume_score DECIMAL(5,2),
    trading_volume_max DECIMAL(5,2),
    trading_volume_percentage DECIMAL(5,2),
    
    liquidity_score DECIMAL(5,2),
    liquidity_max DECIMAL(5,2),
    liquidity_percentage DECIMAL(5,2),
    
    whale_transactions_score DECIMAL(5,2),
    whale_transactions_max DECIMAL(5,2),
    whale_transactions_percentage DECIMAL(5,2),
    
    token_distribution_score DECIMAL(5,2),
    token_distribution_max DECIMAL(5,2),
    token_distribution_percentage DECIMAL(5,2),
    
    pre_sale_vesting_score DECIMAL(5,2),
    pre_sale_vesting_max DECIMAL(5,2),
    pre_sale_vesting_percentage DECIMAL(5,2),
    
    smart_contract_audit_score DECIMAL(5,2),
    smart_contract_audit_max DECIMAL(5,2),
    smart_contract_audit_percentage DECIMAL(5,2),
    
    -- Additional data points
    market_cap DECIMAL(18,2),
    circulating_supply DECIMAL(18,8),
    total_supply DECIMAL(18,8),
    trading_volume_24h DECIMAL(18,2),
    
    -- Vesting data
    upcoming_unlocks INTEGER,
    days_to_next_unlock INTEGER,
    unlock_percentage DECIMAL(5,2),
    
    -- Audit data
    audits_found INTEGER,
    vulnerabilities_critical INTEGER,
    vulnerabilities_major INTEGER,
    
    -- Raw JSON data for future reference
    raw_data JSONB,
    
    -- Constraints
    UNIQUE(symbol, analysis_date)
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_{table}_symbol ON {table}(symbol);
CREATE INDEX IF NOT EXISTS idx_{table}_date ON {table}(analysis_date);
CREATE INDEX IF NOT EXISTS idx_{table}_recommendation ON {table}(recommendation);

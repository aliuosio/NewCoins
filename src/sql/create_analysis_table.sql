-- SQL script to create the crypto_analysis table schema
-- This table stores the results of cryptocurrency analysis

-- INDICATOR SCORING EXPLANATIONS:
-- trading_volume: Awards up to 15 points for having at least $1M in 24h trading volume.
-- liquidity: Awards up to 15 points for having tight spread (<0.5%) and deep order book.
-- whale_transactions: Awards up to 10 points for having >50% whale buys and no mass sell-offs.
-- token_distribution: Awards up to 10 points for well-distributed token supply with active community engagement.
-- pre_sale_vesting: Awards up to 10 points for having no major unlocks in the near future.
-- smart_contract_audit: Awards up to 10 points for having multiple audits by top firms, no vulnerabilities, and mature contract.

DROP TABLE IF EXISTS {table} CASCADE;

CREATE TABLE IF NOT EXISTS {table} (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    analysis_date TIMESTAMPTZ NOT NULL,
    
    -- Overall scores (max total: 70 points)
    -- Recommendation thresholds:
    -- >= 80%: STRONG BUY - High potential for growth
    -- >= 70%: BUY - Good potential for growth
    -- >= 60%: HOLD - Moderate potential
    -- >= 50%: WATCH - Some concerns
    -- < 50%: AVOID - Significant concerns
    total_score DECIMAL(5,2) NOT NULL,
    recommendation TEXT NOT NULL,
    
    -- Individual indicator scores
    -- Trading Volume (15 points): Measures 24h trading volume
    -- Full score for volume >= $1M, proportional below that
    trading_volume_score DECIMAL(5,2),
    
    -- Liquidity (15 points): Measures spread and market depth
    -- Considers volatility-adjusted spread and market impact
    -- Spread target: 0.5% or less for full points
    liquidity_score DECIMAL(5,2),
    
    -- Whale Transactions (10 points): Analyzes volume spikes and price patterns
    -- Detects accumulation/distribution patterns and buy/sell ratio
    -- Higher score for >50% buy ratio and no consecutive price drops
    whale_transactions_score DECIMAL(5,2),
    
    -- Token Distribution (10 points): Analyzes token distribution metrics
    -- Considers circulation ratio, Gini coefficient, holder diversity
    -- Higher score for more equal distribution and active community
    token_distribution_score DECIMAL(5,2),
    
    -- Pre-Sale Vesting (10 points): Evaluates token vesting schedule
    -- Analyzes upcoming unlocks and their potential market impact
    -- Lower score for imminent large unlocks with high market impact
    pre_sale_vesting_score DECIMAL(5,2),
    
    -- Smart Contract Audit (10 points): Evaluates contract security
    -- Considers audits, vulnerabilities, code quality, and security practices
    -- Higher score for multiple audits by reputable firms and no vulnerabilities
    smart_contract_audit_score DECIMAL(5,2),
    
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

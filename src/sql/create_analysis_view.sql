-- SQL script to create a materialized view that combines technical and social indicators
-- and calculates the overall score with categories

-- Drop existing view if it exists
DROP MATERIALIZED VIEW IF EXISTS analysis_summary;

-- Create materialized view
CREATE MATERIALIZED VIEW analysis_summary AS
SELECT 
    t.symbol,
    t.analysis_date,
    
    -- Technical indicators
    t.trading_volume_score,
    t.liquidity_score,
    t.whale_transactions_score,
    t.token_distribution_score,
    t.pre_sale_vesting_score,
    t.smart_contract_audit_score,
    
    -- Social indicators
    s.social_volume_score,
    s.sentiment_analysis_score,
    s.developer_activity_score,
    s.total_social_score,
    
    -- Calculate total technical score (max 70 points)
    (
        COALESCE(t.trading_volume_score, 0) +
        COALESCE(t.liquidity_score, 0) +
        COALESCE(t.whale_transactions_score, 0) +
        COALESCE(t.token_distribution_score, 0) +
        COALESCE(t.pre_sale_vesting_score, 0) +
        COALESCE(t.smart_contract_audit_score, 0)
    ) as total_technical_score,
    
    -- Calculate total score (max 100 points)
    (
        COALESCE(t.trading_volume_score, 0) +
        COALESCE(t.liquidity_score, 0) +
        COALESCE(t.whale_transactions_score, 0) +
        COALESCE(t.token_distribution_score, 0) +
        COALESCE(t.pre_sale_vesting_score, 0) +
        COALESCE(t.smart_contract_audit_score, 0) +
        COALESCE(s.total_social_score, 0)
    ) as total_score,
    
    -- Calculate percentage score
    (
        (
            COALESCE(t.trading_volume_score, 0) +
            COALESCE(t.liquidity_score, 0) +
            COALESCE(t.whale_transactions_score, 0) +
            COALESCE(t.token_distribution_score, 0) +
            COALESCE(t.pre_sale_vesting_score, 0) +
            COALESCE(t.smart_contract_audit_score, 0) +
            COALESCE(s.total_social_score, 0)
        ) * 100.0 / 100
    ) as score_percentage,
    
    -- Calculate recommendation category
    CASE 
        WHEN (
            COALESCE(t.trading_volume_score, 0) +
            COALESCE(t.liquidity_score, 0) +
            COALESCE(t.whale_transactions_score, 0) +
            COALESCE(t.token_distribution_score, 0) +
            COALESCE(t.pre_sale_vesting_score, 0) +
            COALESCE(t.smart_contract_audit_score, 0) +
            COALESCE(s.total_social_score, 0)
        ) >= 80 THEN 'STRONG BUY - High potential for growth'
        WHEN (
            COALESCE(t.trading_volume_score, 0) +
            COALESCE(t.liquidity_score, 0) +
            COALESCE(t.whale_transactions_score, 0) +
            COALESCE(t.token_distribution_score, 0) +
            COALESCE(t.pre_sale_vesting_score, 0) +
            COALESCE(t.smart_contract_audit_score, 0) +
            COALESCE(s.total_social_score, 0)
        ) >= 70 THEN 'BUY - Good potential for growth'
        WHEN (
            COALESCE(t.trading_volume_score, 0) +
            COALESCE(t.liquidity_score, 0) +
            COALESCE(t.whale_transactions_score, 0) +
            COALESCE(t.token_distribution_score, 0) +
            COALESCE(t.pre_sale_vesting_score, 0) +
            COALESCE(t.smart_contract_audit_score, 0) +
            COALESCE(s.total_social_score, 0)
        ) >= 60 THEN 'HOLD - Moderate potential'
        WHEN (
            COALESCE(t.trading_volume_score, 0) +
            COALESCE(t.liquidity_score, 0) +
            COALESCE(t.whale_transactions_score, 0) +
            COALESCE(t.token_distribution_score, 0) +
            COALESCE(t.pre_sale_vesting_score, 0) +
            COALESCE(t.smart_contract_audit_score, 0) +
            COALESCE(s.total_social_score, 0)
        ) >= 50 THEN 'WATCH - Some concerns'
        ELSE 'AVOID - Significant concerns'
    END as recommendation,
    
    -- Raw data from both tables
    t.raw_data as technical_data,
    s.raw_data as social_data

FROM analyse_technical t
LEFT JOIN analyse_social s ON t.symbol = s.symbol AND t.analysis_date = s.analysis_date

WITH NO DATA;

-- Create index for better query performance
CREATE INDEX idx_analysis_summary_symbol_date ON analysis_summary(symbol, analysis_date);

-- Function to refresh the materialized view
CREATE OR REPLACE FUNCTION refresh_analysis_summary()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW analysis_summary;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT SELECT ON analysis_summary TO SpecialOsio;

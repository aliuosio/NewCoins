-- SQL script to create a materialized view that combines technical and social indicators
-- and calculates the overall score with categories

-- Technical indicators (70 points total):
-- trading_volume: 15 points - >$1M in first 24h on another exchange
-- liquidity: 15 points - Tight spread (<0.5%), deep order book
-- whale_transactions: 10 points - >50% whale buys, no mass sell-offs
-- token_distribution: 10 points - No single wallet holding >10%
-- smart_contract_audit: 10 points - Certik/SlowMist audit, no vulnerabilities
-- pre_sale_vesting: 10 points - No major unlocks in next 30 days

-- Social indicators (30 points total):
-- social_volume_score: 10 points - 1000+ mentions, growing trend
-- sentiment_analysis_score: 10 points - >70% positive sentiment
-- developer_activity_score: 5 points - Trending upwards
-- community_growth_score: 5 points - >500 active members, constant discussion

-- Drop existing view if it exists
DROP MATERIALIZED VIEW IF EXISTS analysis_summary;

-- Create regular view
CREATE OR REPLACE VIEW analysis_summary AS
SELECT 
    t.symbol,
    
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
    s.community_growth_score,
    
    -- Calculate total social score (max 30 points)
    (
        COALESCE(s.social_volume_score, 0) +
        COALESCE(s.sentiment_analysis_score, 0) +
        COALESCE(s.developer_activity_score, 0) +
        COALESCE(s.community_growth_score, 0)
    ) as total_social_score,
    
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
        COALESCE(s.social_volume_score, 0) +
        COALESCE(s.sentiment_analysis_score, 0) +
        COALESCE(s.developer_activity_score, 0) +
        COALESCE(s.community_growth_score, 0)
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
            COALESCE(s.social_volume_score, 0) +
            COALESCE(s.sentiment_analysis_score, 0) +
            COALESCE(s.developer_activity_score, 0) +
            COALESCE(s.community_growth_score, 0)
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
            COALESCE(s.social_volume_score, 0) +
            COALESCE(s.sentiment_analysis_score, 0) +
            COALESCE(s.developer_activity_score, 0) +
            COALESCE(s.community_growth_score, 0)
        ) >= 80 THEN 'STRONG BUY - High potential for growth'
        WHEN (
            COALESCE(t.trading_volume_score, 0) +
            COALESCE(t.liquidity_score, 0) +
            COALESCE(t.whale_transactions_score, 0) +
            COALESCE(t.token_distribution_score, 0) +
            COALESCE(t.pre_sale_vesting_score, 0) +
            COALESCE(t.smart_contract_audit_score, 0) +
            COALESCE(s.social_volume_score, 0) +
            COALESCE(s.sentiment_analysis_score, 0) +
            COALESCE(s.developer_activity_score, 0) +
            COALESCE(s.community_growth_score, 0)
        ) >= 70 THEN 'BUY - Good potential for growth'
        WHEN (
            COALESCE(t.trading_volume_score, 0) +
            COALESCE(t.liquidity_score, 0) +
            COALESCE(t.whale_transactions_score, 0) +
            COALESCE(t.token_distribution_score, 0) +
            COALESCE(t.pre_sale_vesting_score, 0) +
            COALESCE(t.smart_contract_audit_score, 0) +
            COALESCE(s.social_volume_score, 0) +
            COALESCE(s.sentiment_analysis_score, 0) +
            COALESCE(s.developer_activity_score, 0) +
            COALESCE(s.community_growth_score, 0)
        ) >= 60 THEN 'HOLD - Moderate potential'
        WHEN (
            COALESCE(t.trading_volume_score, 0) +
            COALESCE(t.liquidity_score, 0) +
            COALESCE(t.whale_transactions_score, 0) +
            COALESCE(t.token_distribution_score, 0) +
            COALESCE(t.pre_sale_vesting_score, 0) +
            COALESCE(t.smart_contract_audit_score, 0) +
            COALESCE(s.social_volume_score, 0) +
            COALESCE(s.sentiment_analysis_score, 0) +
            COALESCE(s.developer_activity_score, 0) +
            COALESCE(s.community_growth_score, 0)
        ) >= 50 THEN 'WATCH - Some concerns'
        ELSE 'AVOID - Significant concerns'
    END as recommendation
FROM analyse_technical t
LEFT JOIN analyse_social s ON t.symbol = s.symbol

-- Regular views don't need WITH DATA

-- Note: Indexes are not needed for regular views as they are computed on-the-fly

-- Regular views don't need refresh functions

-- Comments for the view and calculated fields
-- View: Real-time view of cryptocurrency risk assessment combining technical (70 points) and social (30 points) indicators with recommendation categories
-- Column total_technical_score: Sum of all technical indicator scores (max 70 points) including trading volume (15), liquidity (15), whale transactions (10), token distribution (10), pre-sale vesting (10), and smart contract audit (10)
-- Column total_social_score: Sum of all social indicator scores (max 30 points) including social volume (10), sentiment analysis (10), developer activity (5), and community growth (5)
-- Column total_score: Combined total of all technical and social indicators (max 100 points)
-- Column score_percentage: Total score expressed as a percentage (0-100%)
-- Column recommendation: Investment recommendation based on total score: STRONG BUY (≥80), BUY (≥70), HOLD (≥60), WATCH (≥50), AVOID (<50)

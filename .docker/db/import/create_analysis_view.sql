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
-- google_trends_score: 5 points - Strong uptrend in search interest
-- sentiment_analysis_score: 10 points - >70% positive sentiment
-- developer_activity_score: 10 points - Trending upwards
-- community_growth_score: 5 points - >500 active members, constant discussion

-- Create regular view with optimized structure using CTEs
CREATE OR REPLACE VIEW analysis_summary AS
WITH score_components AS (
  SELECT 
    t.symbol,
    COALESCE(t.trading_volume_score, 0) as trading_volume_score,
    COALESCE(t.liquidity_score, 0) as liquidity_score,
    COALESCE(t.whale_transactions_score, 0) as whale_transactions_score,
    COALESCE(t.token_distribution_score, 0) as token_distribution_score,
    COALESCE(t.pre_sale_vesting_score, 0) as pre_sale_vesting_score,
    COALESCE(t.smart_contract_audit_score, 0) as smart_contract_audit_score,
    COALESCE(s.google_trends_score, 0) as google_trends_score,
    COALESCE(s.sentiment_analysis_score, 0) as sentiment_analysis_score,
    COALESCE(s.developer_activity_score, 0) as developer_activity_score,
    COALESCE(s.community_growth_score, 0) as community_growth_score
  FROM analyse_technical t
  LEFT JOIN analyse_social s ON t.symbol = s.symbol
),
calculated_scores AS (
  SELECT 
    *,
    (google_trends_score + sentiment_analysis_score + developer_activity_score + community_growth_score) as total_social_score,
    (trading_volume_score + liquidity_score + whale_transactions_score + token_distribution_score + pre_sale_vesting_score + smart_contract_audit_score) as total_technical_score,
    (trading_volume_score + liquidity_score + whale_transactions_score + token_distribution_score + pre_sale_vesting_score + smart_contract_audit_score + google_trends_score + sentiment_analysis_score + developer_activity_score + community_growth_score) as total_score
  FROM score_components
)
SELECT
  symbol,
  trading_volume_score,
  liquidity_score,
  whale_transactions_score,
  token_distribution_score,
  pre_sale_vesting_score,
  smart_contract_audit_score,
  google_trends_score,
  sentiment_analysis_score,
  developer_activity_score,
  community_growth_score,
  total_social_score,
  total_technical_score,
  total_score,
  total_score as score_percentage,
  CASE 
    WHEN total_score >= 50 THEN (SELECT RECOMMEND_BUY_LABEL FROM (SELECT current_setting('RECOMMEND_BUY_LABEL', true) as RECOMMEND_BUY_LABEL) as env) || ' - Good potential for growth'
    WHEN total_score >= 40 THEN (SELECT RECOMMEND_HOLD_LABEL FROM (SELECT current_setting('RECOMMEND_HOLD_LABEL', true) as RECOMMEND_HOLD_LABEL) as env) || ' - Moderate potential'
    WHEN total_score >= 30 THEN (SELECT RECOMMEND_WATCH_LABEL FROM (SELECT current_setting('RECOMMEND_WATCH_LABEL', true) as RECOMMEND_WATCH_LABEL) as env) || ' - Some concerns'
    ELSE (SELECT RECOMMEND_AVOID_LABEL FROM (SELECT current_setting('RECOMMEND_AVOID_LABEL', true) as RECOMMEND_AVOID_LABEL) as env) || ' - Significant concerns'
  END as recommendation

-- Regular views don't need WITH DATA

-- Note: Indexes are not needed for regular views as they are computed on-the-fly

-- Regular views don't need refresh functions

-- Comments for the view and calculated fields
-- View: Real-time view of cryptocurrency risk assessment combining technical (70 points) and social (30 points) indicators with recommendation categories
-- Column total_technical_score: Sum of all technical indicator scores (max 70 points) including trading volume (15), liquidity (15), whale transactions (10), token distribution (10), pre-sale vesting (10), and smart contract audit (10)
-- Column total_social_score: Sum of all social indicator scores (max 30 points) including google trends (5), sentiment analysis (10), developer activity (10), and community growth (5)
-- Column total_score: Combined total of all technical and social indicators (max 100 points)
-- Column score_percentage: Total score expressed as a percentage (0-100%)
-- Column recommendation: Investment recommendation based on total score: STRONG BUY (≥80), BUY (≥70), HOLD (≥60), WATCH (≥50), AVOID (<50)

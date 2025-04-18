-- SQL script to create the analyse_social table schema
-- Usage: Placeholder {table} is formatted in Python before execution
-- This table tracks social metrics and sentiment for cryptocurrencies

CREATE TABLE IF NOT EXISTS {table} (
    -- Primary key and relationship
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,                   -- Trading symbol (e.g., BTC)
    analysis_date TIMESTAMPTZ NOT NULL,     -- When the analysis was performed
    
    -- Social Indicators (max total: 30 points)
    -- Social indicators evaluate community engagement, sentiment, and growth
    
    -- Social Volume (10 points): Measures mentions and discussions
    -- Full score for high discussion volume across platforms
    social_volume_score DECIMAL(5,2),       -- Score for social media mentions and discussion volume
    
    -- Sentiment Analysis (10 points): Evaluates positive vs negative sentiment
    -- Higher score for predominantly positive sentiment
    sentiment_analysis_score DECIMAL(5,2),  -- Score for overall sentiment analysis
    
    -- Developer Activity (10 points): Tracks GitHub commits and contributors
    -- Higher score for active development and growing contributor base
    developer_activity_score DECIMAL(5,2),  -- Score for developer activity
    
    -- Overall social score
    total_social_score DECIMAL(5,2),        -- Sum of all social indicator scores
    
    -- Raw data for future reference
    raw_data JSONB,                         -- Detailed raw data in JSON format
    
    -- Constraints
    UNIQUE(symbol, analysis_date),
    
    -- Indexes for performance
    CONSTRAINT fk_symbol FOREIGN KEY(symbol) REFERENCES {coins_table}(symbol)
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_social_symbol ON {table} (symbol);
CREATE INDEX IF NOT EXISTS idx_social_date ON {table} (analysis_date);

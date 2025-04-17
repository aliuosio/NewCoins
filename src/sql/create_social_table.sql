-- SQL script to create the social indicators table schema
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
    mentions_24h INTEGER,                   -- Number of mentions in the last 24 hours
    mentions_change_pct DECIMAL(5,2),       -- Percentage change in mentions
    
    -- Sentiment Analysis (10 points): Evaluates positive vs negative sentiment
    -- Higher score for predominantly positive sentiment
    sentiment_score DECIMAL(5,2),           -- Score for overall sentiment analysis
    sentiment_positive_pct DECIMAL(5,2),    -- Percentage of positive sentiment
    sentiment_negative_pct DECIMAL(5,2),    -- Percentage of negative sentiment
    sentiment_neutral_pct DECIMAL(5,2),     -- Percentage of neutral sentiment
    
    -- Developer Activity (10 points): Tracks GitHub commits and contributors
    -- Higher score for active development and growing contributor base
    developer_score DECIMAL(5,2),           -- Score for developer activity
    github_commits_4w INTEGER,              -- GitHub commits in last 4 weeks
    github_contributors INTEGER,            -- Number of active contributors
    github_stars INTEGER,                   -- Number of GitHub stars
    
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

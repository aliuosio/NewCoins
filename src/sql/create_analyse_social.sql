-- Drop existing table and trigger
DROP TABLE IF EXISTS {table} CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column_{table} CASCADE;

-- Social indicators scoring criteria

-- Create table
CREATE TABLE IF NOT EXISTS {table} (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,                   
    social_volume_score DECIMAL(5,2),       
    sentiment_analysis_score DECIMAL(5,2),  
    developer_activity_score DECIMAL(5,2),  
    community_growth_score DECIMAL(5,2),    
    
    analysis_date DATE NOT NULL DEFAULT CURRENT_DATE,    
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(symbol) -- Only one record per coin
);

-- Add column comments
COMMENT ON COLUMN {table}.social_volume_score IS '10 points - 1000+ mentions, growing trend';
COMMENT ON COLUMN {table}.sentiment_analysis_score IS '10 points - >70% positive sentiment';
COMMENT ON COLUMN {table}.developer_activity_score IS '5 points - Trending upwards';
COMMENT ON COLUMN {table}.community_growth_score IS '5 points - >500 active members, constant discussion';

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_social_symbol ON {table} (symbol);
CREATE INDEX IF NOT EXISTS idx_social_date ON {table} (analysis_date);

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

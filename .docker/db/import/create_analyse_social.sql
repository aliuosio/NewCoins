-- Drop existing table and trigger
DROP TABLE IF EXISTS analyse_social CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column_analyse_social CASCADE;

-- Social indicators scoring criteria

-- Create table
CREATE TABLE IF NOT EXISTS analyse_social (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,                   
    social_volume_score DECIMAL(5,2),       
    sentiment_analysis_score DECIMAL(5,2),  
    developer_activity_score DECIMAL(5,2),  
    community_growth_score DECIMAL(5,2),    
    

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(symbol) -- Only one record per coin
);

-- Add column comments
COMMENT ON COLUMN analyse_social.social_volume_score IS '10 points - 1000+ mentions, growing trend';
COMMENT ON COLUMN analyse_social.sentiment_analysis_score IS '10 points - >70% positive sentiment';
COMMENT ON COLUMN analyse_social.developer_activity_score IS '5 points - Trending upwards';
COMMENT ON COLUMN analyse_social.community_growth_score IS '5 points - >500 active members, constant discussion';

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_social_symbol ON analyse_social (symbol);

-- Create trigger function to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column_analyse_social()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger to table
CREATE TRIGGER set_updated_at_analyse_social
BEFORE UPDATE ON analyse_social
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column_analyse_social();

-- Nexzy Comprehensive Upgrades Migration
-- Run this in Supabase SQL Editor to add new fields

-- Add updated_at column if it doesn't exist (required by backend)
ALTER TABLE alerts ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Add vulnerability_score to alerts table (for displaying 0-100 RoBERTa scores)
ALTER TABLE alerts ADD COLUMN IF NOT EXISTS vulnerability_score FLOAT DEFAULT 0.0;

-- Add AI analysis depth fields to alerts
ALTER TABLE alerts ADD COLUMN IF NOT EXISTS ai_signals TEXT[] DEFAULT '{}';
ALTER TABLE alerts ADD COLUMN IF NOT EXISTS ai_confidence FLOAT DEFAULT 0.0;
ALTER TABLE alerts ADD COLUMN IF NOT EXISTS ai_mitigation TEXT DEFAULT '';

-- Add content snippet storage to scan_results
ALTER TABLE scan_results ADD COLUMN IF NOT EXISTS content_snippet TEXT DEFAULT '';

-- Add content snippet and source URL to alerts table
ALTER TABLE alerts ADD COLUMN IF NOT EXISTS content_snippet TEXT DEFAULT '';
ALTER TABLE alerts ADD COLUMN IF NOT EXISTS source_url TEXT DEFAULT '';

-- Create index for vulnerability_score lookups
CREATE INDEX IF NOT EXISTS idx_alerts_vulnerability_score ON alerts(vulnerability_score DESC);

-- Update existing alerts to extract vulnerability_score from description (migration helper)
-- This extracts the score from "Vulnerability Score: XX.X/100" in descriptions
UPDATE alerts 
SET vulnerability_score = (
    SELECT CAST(
        regexp_replace(
            substring(description from 'Vulnerability Score: ([0-9.]+)/100'),
            '[^0-9.]',
            '',
            'g'
        ) AS FLOAT
    )
)
WHERE description LIKE '%Vulnerability Score:%' AND vulnerability_score = 0.0;

-- Comment on new columns for documentation
COMMENT ON COLUMN alerts.vulnerability_score IS 'RoBERTa AI vulnerability score (0-100 scale)';
COMMENT ON COLUMN alerts.ai_signals IS 'Array of detected security signals (credentials, PII, etc)';
COMMENT ON COLUMN alerts.ai_confidence IS 'AI confidence level in the assessment (0.0-1.0)';
COMMENT ON COLUMN alerts.ai_mitigation IS 'AI-generated mitigation recommendations';
COMMENT ON COLUMN alerts.content_snippet IS 'First 500 characters of paste content for preview';
COMMENT ON COLUMN alerts.source_url IS 'Direct URL to the source paste/leak';
COMMENT ON COLUMN scan_results.content_snippet IS 'First 500 characters of paste content for preview';

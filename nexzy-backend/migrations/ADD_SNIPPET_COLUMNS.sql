-- Add content snippet and source URL columns to alerts table
ALTER TABLE alerts ADD COLUMN IF NOT EXISTS content_snippet TEXT DEFAULT '';
ALTER TABLE alerts ADD COLUMN IF NOT EXISTS source_url TEXT DEFAULT '';

-- Update existing alerts to extract source_url from description
UPDATE alerts 
SET source_url = substring(description from 'Source URL: (https?://[^\n]+)')
WHERE source_url = '' AND description LIKE '%Source URL:%';

-- Add comments
COMMENT ON COLUMN alerts.content_snippet IS 'First 500 characters of paste content for preview';
COMMENT ON COLUMN alerts.source_url IS 'Direct URL to the source paste/leak';

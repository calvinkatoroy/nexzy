-- ============================================================================
-- ADD credentials_found COLUMN TO scans TABLE
-- ============================================================================
-- This migration adds a column to track how many credentials were found
-- in each scan, which is needed for the AlertsPage severity calculation.

ALTER TABLE public.scans 
ADD COLUMN IF NOT EXISTS credentials_found INTEGER NOT NULL DEFAULT 0;

-- Create index for faster queries on high-risk scans
CREATE INDEX IF NOT EXISTS idx_scans_credentials_found 
ON public.scans(credentials_found DESC);

-- Verify the column was added
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'scans' 
AND column_name = 'credentials_found';

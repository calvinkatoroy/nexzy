-- Nexzy Database Schema
-- Run this in Supabase SQL Editor

-- Create scans table
CREATE TABLE IF NOT EXISTS scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'queued',
    progress FLOAT DEFAULT 0.0,
    total_results INT DEFAULT 0,
    credentials_found INT DEFAULT 0,
    urls TEXT[] NOT NULL,
    options JSONB DEFAULT '{}',
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create scan_results table
CREATE TABLE IF NOT EXISTS scan_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id UUID NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    source TEXT NOT NULL,
    author TEXT,
    relevance_score FLOAT NOT NULL,
    emails TEXT[] DEFAULT '{}',
    target_emails TEXT[] DEFAULT '{}',
    has_credentials BOOLEAN DEFAULT false,
    content_preview TEXT,
    found_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'investigating', 'resolved', 'false_positive')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_scans_user_id ON scans(user_id);
CREATE INDEX idx_scans_status ON scans(status);
CREATE INDEX idx_scan_results_scan_id ON scan_results(scan_id);
CREATE INDEX idx_scan_results_has_credentials ON scan_results(has_credentials);
CREATE INDEX idx_alerts_user_id ON alerts(user_id);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_status ON alerts(status);

-- Enable Row Level Security
ALTER TABLE scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE scan_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

-- RLS Policies for scans
CREATE POLICY "Users can view own scans" ON scans
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own scans" ON scans
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own scans" ON scans
    FOR UPDATE USING (auth.uid() = user_id);

-- RLS Policies for scan_results
CREATE POLICY "Users can view own scan results" ON scan_results
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM scans 
            WHERE scans.id = scan_results.scan_id 
            AND scans.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own scan results" ON scan_results
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM scans 
            WHERE scans.id = scan_results.scan_id 
            AND scans.user_id = auth.uid()
        )
    );

-- RLS Policies for alerts
CREATE POLICY "Users can view own alerts" ON alerts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own alerts" ON alerts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own alerts" ON alerts
    FOR UPDATE USING (auth.uid() = user_id);

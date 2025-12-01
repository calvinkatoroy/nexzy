# Nexzy Backend - Database Schema

This document describes the required Supabase database schema for the Nexzy backend.

## Required Tables

Run this SQL in your Supabase SQL Editor:

```sql
-- ============================================================================
-- NEXZY DATABASE SCHEMA
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. SCANS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.scans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'completed', 'failed')),
    progress FLOAT NOT NULL DEFAULT 0.0 CHECK (progress >= 0.0 AND progress <= 1.0),
    total_results INTEGER NOT NULL DEFAULT 0,
    credentials_found INTEGER NOT NULL DEFAULT 0,
    urls JSONB NOT NULL DEFAULT '[]'::jsonb,
    options JSONB NOT NULL DEFAULT '{}'::jsonb,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX idx_scans_user_id ON public.scans(user_id);
CREATE INDEX idx_scans_status ON public.scans(status);
CREATE INDEX idx_scans_created_at ON public.scans(created_at DESC);

-- ============================================================================
-- 2. SCAN RESULTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.scan_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scan_id UUID NOT NULL REFERENCES public.scans(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    source TEXT NOT NULL,
    author TEXT NOT NULL DEFAULT 'unknown',
    relevance_score FLOAT NOT NULL CHECK (relevance_score >= 0.0 AND relevance_score <= 1.0),
    emails JSONB NOT NULL DEFAULT '[]'::jsonb,
    target_emails JSONB NOT NULL DEFAULT '[]'::jsonb,
    has_credentials BOOLEAN NOT NULL DEFAULT false,
    found_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for faster queries
CREATE INDEX idx_scan_results_scan_id ON public.scan_results(scan_id);
CREATE INDEX idx_scan_results_user_id ON public.scan_results(user_id);
CREATE INDEX idx_scan_results_relevance ON public.scan_results(relevance_score DESC);
CREATE INDEX idx_scan_results_found_at ON public.scan_results(found_at DESC);

-- ============================================================================
-- 3. AUTO-UPDATE TIMESTAMP TRIGGER
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for scans table
CREATE TRIGGER update_scans_updated_at
    BEFORE UPDATE ON public.scans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 4. ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS
ALTER TABLE public.scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scan_results ENABLE ROW LEVEL SECURITY;

-- Scans policies
CREATE POLICY "Users can view their own scans"
    ON public.scans FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own scans"
    ON public.scans FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own scans"
    ON public.scans FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own scans"
    ON public.scans FOR DELETE
    USING (auth.uid() = user_id);

-- Scan results policies
CREATE POLICY "Users can view their own scan results"
    ON public.scan_results FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own scan results"
    ON public.scan_results FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own scan results"
    ON public.scan_results FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- 5. OPTIONAL: USER PROFILES TABLE (if not exists)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    organization TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own profile"
    ON public.user_profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON public.user_profiles FOR UPDATE
    USING (auth.uid() = id);

-- Auto-create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (id, email, full_name)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- ============================================================================
-- 6. OPTIONAL: ALERTS TABLE (for high-value findings)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    scan_result_id UUID REFERENCES public.scan_results(id) ON DELETE SET NULL,
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'acknowledged', 'resolved', 'false_positive')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_alerts_user_id ON public.alerts(user_id);
CREATE INDEX idx_alerts_status ON public.alerts(status);
CREATE INDEX idx_alerts_severity ON public.alerts(severity);

ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own alerts"
    ON public.alerts FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own alerts"
    ON public.alerts FOR UPDATE
    USING (auth.uid() = user_id);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify tables were created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('scans', 'scan_results', 'user_profiles', 'alerts');

-- Verify RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('scans', 'scan_results', 'user_profiles', 'alerts');
```

## Schema Overview

### `scans` Table
Stores scan job metadata and status.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to auth.users |
| status | TEXT | 'queued', 'running', 'completed', 'failed' |
| progress | FLOAT | 0.0 to 1.0 |
| total_results | INTEGER | Number of results found |
| credentials_found | INTEGER | Number of credentials detected |
| urls | JSONB | Array of URLs to scan |
| options | JSONB | Scan configuration options |
| error | TEXT | Error message if failed |
| created_at | TIMESTAMPTZ | When scan was created |
| updated_at | TIMESTAMPTZ | Last update time |

### `scan_results` Table
Stores individual discovered items from scans.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| scan_id | UUID | Foreign key to scans |
| user_id | UUID | Foreign key to auth.users |
| url | TEXT | URL where item was found |
| source | TEXT | Source site (e.g., 'pastebin.com') |
| author | TEXT | Author of the paste |
| relevance_score | FLOAT | 0.0 to 1.0 relevance score |
| emails | JSONB | Array of all extracted emails |
| target_emails | JSONB | Array of target domain emails |
| has_credentials | BOOLEAN | Whether credentials were detected |
| found_at | TIMESTAMPTZ | When item was discovered |

### `user_profiles` Table (Optional)
Extended user information.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key (matches auth.users.id) |
| email | TEXT | User email |
| full_name | TEXT | User's full name |
| organization | TEXT | Organization name |
| created_at | TIMESTAMPTZ | Profile creation time |
| updated_at | TIMESTAMPTZ | Last update time |

### `alerts` Table (Optional)
High-priority notifications for critical findings.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to auth.users |
| scan_result_id | UUID | Related scan result |
| severity | TEXT | 'low', 'medium', 'high', 'critical' |
| title | TEXT | Alert title |
| description | TEXT | Alert details |
| status | TEXT | 'new', 'acknowledged', 'resolved', 'false_positive' |
| created_at | TIMESTAMPTZ | Alert creation time |
| resolved_at | TIMESTAMPTZ | When alert was resolved |

## Security Features

1. **Row Level Security (RLS)**: Users can only access their own data
2. **CASCADE DELETE**: Deleting a user removes all their scans and results
3. **Auto-timestamps**: `updated_at` automatically updates on changes
4. **Check constraints**: Validates data integrity (e.g., progress 0.0-1.0)
5. **Indexes**: Optimizes query performance

## Applying the Schema

1. Log in to [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Go to **SQL Editor**
4. Copy the SQL above
5. Click **Run** to execute

## Verifying Installation

Run these queries to verify:

```sql
-- Check tables exist
SELECT * FROM public.scans LIMIT 1;
SELECT * FROM public.scan_results LIMIT 1;

-- Check RLS is enabled
SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';

-- Check policies exist
SELECT * FROM pg_policies WHERE schemaname = 'public';
```

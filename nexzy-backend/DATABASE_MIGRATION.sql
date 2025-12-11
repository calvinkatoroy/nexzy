-- ========================================
-- NEXZY DATABASE MIGRATION
-- Multi-University Support Feature
-- ========================================
-- Run this in Supabase SQL Editor
-- Project: oyziawmetogvilefpepl
-- URL: https://app.supabase.com/project/oyziawmetogvilefpepl/editor
--
-- This migration adds support for:
-- 1. Custom target domains per user
-- 2. Custom search keywords per user
-- 3. Multi-university presets (UI, ITB, UGM, etc.)
-- ========================================

-- Step 1: Add new columns to user_profiles table
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS target_domain TEXT DEFAULT 'ui.ac.id',
ADD COLUMN IF NOT EXISTS target_keywords JSONB DEFAULT '["ui.ac.id", "universitas indonesia"]'::jsonb,
ADD COLUMN IF NOT EXISTS organization TEXT DEFAULT 'Universitas Indonesia',
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Step 1b: Add logs column to scans table for storing scan execution logs
ALTER TABLE scans
ADD COLUMN IF NOT EXISTS logs JSONB DEFAULT '[]'::jsonb;

-- Step 2: Update existing rows with default values
UPDATE user_profiles 
SET 
  target_domain = COALESCE(target_domain, 'ui.ac.id'),
  target_keywords = COALESCE(target_keywords, '["ui.ac.id", "universitas indonesia"]'::jsonb),
  organization = COALESCE(organization, 'Universitas Indonesia'),
  updated_at = COALESCE(updated_at, NOW())
WHERE target_domain IS NULL 
   OR target_keywords IS NULL 
   OR organization IS NULL 
   OR updated_at IS NULL;

-- Step 3: Create user_profiles entry for current user if it doesn't exist
-- Replace 'YOUR_USER_ID_HERE' with your actual user ID from auth.users table
-- You can find it by running: SELECT id, email FROM auth.users;
INSERT INTO user_profiles (id, email, target_domain, target_keywords, organization, created_at, updated_at)
SELECT 
  id, 
  email, 
  'ui.ac.id' AS target_domain,
  '["ui.ac.id", "universitas indonesia"]'::jsonb AS target_keywords,
  'Universitas Indonesia' AS organization,
  NOW() AS created_at,
  NOW() AS updated_at
FROM auth.users
WHERE NOT EXISTS (
  SELECT 1 FROM user_profiles WHERE user_profiles.id = auth.users.id
);

-- Step 4: Verify migration
SELECT 
  id, 
  email, 
  target_domain, 
  target_keywords, 
  organization,
  created_at,
  updated_at
FROM user_profiles
ORDER BY created_at DESC;

-- Expected result: All users should have profiles with default values
-- Sample output:
-- id                                   | email                      | target_domain | target_keywords                           | organization
-- -------------------------------------|----------------------------|---------------|------------------------------------------|----------------------
-- 550e8400-e29b-41d4-a716-446655440000 | calvinwkatoroy@gmail.com  | ui.ac.id      | ["ui.ac.id", "universitas indonesia"]    | Universitas Indonesia

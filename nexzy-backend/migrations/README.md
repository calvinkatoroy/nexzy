# Database Migrations

This folder contains SQL migration files for the Nexzy database schema.

## Files

- `supabase_schema.sql` - Initial database schema (in root)
- `DATABASE_MIGRATION.sql` - Core schema updates
- `COMPREHENSIVE_UPGRADES.sql` - AI scoring, vulnerability fields, and dashboard stats
- `ADD_SNIPPET_COLUMNS.sql` - Content snippet and source URL fields for alerts

## Usage

Run these migrations in your Supabase SQL Editor in order:
1. Initial schema (supabase_schema.sql from root)
2. Apply any pending migrations from this folder

Each file is idempotent and uses `IF NOT EXISTS` checks.

-- Migration 003: Add provider column to libraries table
-- This column stores the provider type (github, gitlab, local)

-- Add provider column with default value for existing rows
ALTER TABLE libraries ADD COLUMN provider TEXT DEFAULT 'github';

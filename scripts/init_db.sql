-- GermanGPT Tutor — PostgreSQL initialization
-- Runs once when the container first starts

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search
CREATE EXTENSION IF NOT EXISTS "unaccent"; -- For German umlaut-insensitive search

-- Performance: full-text search index on user memories
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_memories_content_fts
--     ON user_memories USING gin(to_tsvector('german', content));

-- Seed CEFR level progression data (used by analytics)
CREATE TABLE IF NOT EXISTS cefr_progression (
    level VARCHAR(2) PRIMARY KEY,
    min_hours INTEGER NOT NULL,
    max_hours INTEGER NOT NULL,
    description TEXT
);

INSERT INTO cefr_progression VALUES
    ('A1', 0, 80, 'Absolute beginner — survival phrases'),
    ('A2', 80, 200, 'Elementary — basic communication'),
    ('B1', 200, 400, 'Intermediate — independent user'),
    ('B2', 400, 600, 'Upper intermediate — fluent conversations'),
    ('C1', 600, 900, 'Advanced — professional proficiency'),
    ('C2', 900, 1200, 'Mastery — near-native')
ON CONFLICT DO NOTHING;

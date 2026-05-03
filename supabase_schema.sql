
-- Create the 'politicians' table
CREATE TABLE IF NOT EXISTS politicians (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    myneta_id TEXT UNIQUE,
    name TEXT NOT NULL,
    party TEXT,
    constituency TEXT,
    state TEXT,
    education TEXT,
    total_assets NUMERIC,
    total_liabilities NUMERIC,
    criminal_cases INTEGER,
    source_url TEXT UNIQUE,
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create the 'investments' table for general categories
CREATE TABLE IF NOT EXISTS investments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    politician_id UUID REFERENCES politicians(id) ON DELETE CASCADE,
    type TEXT,
    description TEXT,
    amount NUMERIC,
    asset_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create the 'stocks' table for specific equity holdings
CREATE TABLE IF NOT EXISTS stocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    politician_id UUID REFERENCES politicians(id) ON DELETE CASCADE,
    company_name TEXT NOT NULL,
    quantity NUMERIC,
    rate NUMERIC,
    total_value NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_politicians_myneta_id ON politicians(myneta_id);
CREATE INDEX IF NOT EXISTS idx_politicians_name ON politicians(name);
CREATE INDEX IF NOT EXISTS idx_investments_politician_id ON investments(politician_id);
CREATE INDEX IF NOT EXISTS idx_stocks_politician_id ON stocks(politician_id);

-- Create a table for tracking scraping progress
CREATE TABLE IF NOT EXISTS scraping_status (
    id TEXT PRIMARY KEY,
    total_pages INTEGER DEFAULT 167,
    current_page INTEGER DEFAULT 1,
    total_politicians INTEGER DEFAULT 8338,
    processed_politicians INTEGER DEFAULT 0,
    status TEXT DEFAULT 'idle', -- 'running', 'paused', 'idle', 'error'
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Initialize the row
INSERT INTO scraping_status (id, total_pages, total_politicians, status)
VALUES ('loksabha_2024', 167, 8338, 'idle')
ON CONFLICT (id) DO NOTHING;

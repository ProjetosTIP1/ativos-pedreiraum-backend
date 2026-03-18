CREATE TABLE IF NOT EXISTS image_metadata (
    id UUID PRIMARY KEY,
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    name TEXT NOT NULL,
    alt_text TEXT,
    content_type TEXT,
    size INTEGER,
    width INTEGER,
    height INTEGER,
    is_main BOOLEAN DEFAULT FALSE,
    position INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Optimize search for alt text and names (useful for accessibility and fast lookups)
CREATE INDEX IF NOT EXISTS idx_image_metadata_asset_id ON image_metadata(asset_id);
CREATE INDEX IF NOT EXISTS idx_image_metadata_position ON image_metadata(asset_id, position);
CREATE INDEX IF NOT EXISTS idx_image_metadata_name ON image_metadata(name);
CREATE INDEX IF NOT EXISTS idx_image_metadata_alt_text ON image_metadata USING gin(to_tsvector('portuguese', COALESCE(alt_text, '')));

-- Ensure only one main image per asset
CREATE UNIQUE INDEX IF NOT EXISTS idx_image_metadata_only_one_main 
ON image_metadata (asset_id) 
WHERE (is_main = TRUE);

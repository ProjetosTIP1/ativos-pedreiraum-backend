-- Valemix Assets Catalog - Database Schema (DDL)

-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: categories
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(150) UNIQUE NOT NULL,
    parent_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: assets
CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    serial_number VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    condition VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE',
    price DECIMAL(15, 2),
    description TEXT,
    main_image TEXT NOT NULL,
    gallery TEXT[] DEFAULT '{}',
    is_featured BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    specifications JSONB,
    search_vector tsvector,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for full-text search
CREATE INDEX IF NOT EXISTS assets_search_idx ON assets USING GIN(search_vector);

-- Trigger to update search_vector
CREATE OR REPLACE FUNCTION assets_search_trigger() RETURNS trigger AS $$
begin
  new.search_vector :=
    setweight(to_tsvector('portuguese', coalesce(new.name,'')), 'A') ||
    setweight(to_tsvector('portuguese', coalesce(new.model,'')), 'B') ||
    setweight(to_tsvector('portuguese', coalesce(new.brand,'')), 'B') ||
    setweight(to_tsvector('portuguese', coalesce(new.description,'')), 'C');
  return new;
end
$$ LANGUAGE plpgsql;

CREATE TRIGGER assets_search_update BEFORE INSERT OR UPDATE
ON assets FOR EACH ROW EXECUTE FUNCTION assets_search_trigger();

-- Table: configs
CREATE TABLE IF NOT EXISTS app_configs (
    id SERIAL PRIMARY KEY,
    key VARCHAR(50) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Initial configuration
INSERT INTO app_configs (key, value) VALUES ('whatsapp_number', '5500000000000') ON CONFLICT (key) DO NOTHING;
INSERT INTO app_configs (key, value) VALUES ('site_title', 'Valemix Ativos') ON CONFLICT (key) DO NOTHING;

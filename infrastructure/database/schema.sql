-- Valemix Assets Catalog - Database Schema (DDL)

-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- Table: users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    contact TEXT, -- Whatsapp contact
    role VARCHAR(20) NOT NULL DEFAULT 'REGULAR',
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- Table: categories
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- Table: assets
CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    serial_number VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    condition VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    price DECIMAL(15, 2),
    description TEXT,
    rep_contact TEXT, -- Whatsapp contact
    highlighted BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    specifications JSONB,
    created_by_user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    deleted_at TIMESTAMP WITH TIME ZONE NULL
);


CREATE TABLE IF NOT EXISTS image_metadata (
    id UUID PRIMARY KEY,
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    position TEXT DEFAULT 'OUTROS',
    is_main BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- Indexes for image_metadata
CREATE INDEX IF NOT EXISTS idx_image_metadata_asset_id ON image_metadata(asset_id);
CREATE INDEX IF NOT EXISTS idx_image_metadata_position ON image_metadata(asset_id, position);

-- Ensure only one main image per asset
CREATE UNIQUE INDEX IF NOT EXISTS idx_image_metadata_only_one_main 
ON image_metadata (asset_id) 
WHERE (is_main = TRUE);


-- NOTE: Full-text search trigger can be added here in the future
-- when a search_vector column is added to the assets table.

INSERT INTO users (email, full_name, contact, role, hashed_password)
VALUES ('admin@pedreiraumvalemix.com.br', 'Administrador P1', '3199999999', 'ADMIN', '$pbkdf2-sha256$29000$UIrxvlcK4Ryj1PofI4SQMg$2QmlMxiEXk5PeM8aHlm2S4MaeIL2bnLrC/8jMXwb.1M');

INSERT INTO categories (id, name) VALUES (1, 'CAMINHÕES'), (2, 'ESCAVADEIRAS'), (3, 'BRITADORES'), (4, 'MOTONIVELADORAS'), (5, 'PLANTA'), (6, 'PEÇAS'), (7, 'PÁ CARREGADEIRA'), (8, 'OUTROS');
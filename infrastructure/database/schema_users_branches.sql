-- Migration: Add Users and Branches

-- Table: branches
CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    contact_info TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'REGULAR',
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Update Assets table
ALTER TABLE assets ADD COLUMN IF NOT EXISTS branch_id INTEGER REFERENCES branches(id);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS created_by_user_id UUID REFERENCES users(id);

-- Update status constraint if needed (since we added PENDING and REJECTED)
-- Note: In a real migration we might need to handle existing data
ALTER TABLE assets ALTER COLUMN status SET DEFAULT 'PENDING';

-- Insert initial branches
INSERT INTO branches (name, location) VALUES 
('Micon', 'Main Office'),
('P1-BT', 'Branch BT'),
('P1-SB', 'Branch SB')
ON CONFLICT DO NOTHING;

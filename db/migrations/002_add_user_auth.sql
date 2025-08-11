-- Migration: 002_add_user_auth.sql
-- Description: Add authentication fields to users table
-- Created: 2024-01-01

-- Add password_hash column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- Add unique constraint on email if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'users_email_unique' 
        AND table_name = 'users'
    ) THEN
        ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email);
    END IF;
END $$;

-- Add index on password_hash for performance
CREATE INDEX IF NOT EXISTS users_password_hash_idx ON users(password_hash);

-- Add user_id column to cart_items for user-specific carts
ALTER TABLE cart_items ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;

-- Add index on user_id in cart_items
CREATE INDEX IF NOT EXISTS cart_items_user_id_idx ON cart_items(user_id);

-- Update existing cart_items to have a default user (for backward compatibility)
-- In production, you might want to handle this differently
UPDATE cart_items SET user_id = 1 WHERE user_id IS NULL;

-- Make user_id NOT NULL after setting default values
ALTER TABLE cart_items ALTER COLUMN user_id SET NOT NULL; 
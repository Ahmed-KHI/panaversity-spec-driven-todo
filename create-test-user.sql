-- Create test user in backend users table
-- Password: password123
-- Bcrypt hash generated with: python -c "from passlib.hash import bcrypt; print(bcrypt.hash('password123'))"

INSERT INTO users (id, email, password_hash, created_at, updated_at) 
VALUES (
  'b2c3d4e5-f6a7-4b5c-8d9e-0f1a2b3c4d5e',
  'test@hackathon.com',
  '$2b$12$KIXxLQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYjQQBv',
  NOW(),
  NOW()
) ON CONFLICT (email) DO NOTHING;

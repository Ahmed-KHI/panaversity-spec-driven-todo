INSERT INTO users (id, email, password_hash, created_at, updated_at) 
VALUES (
  'a1b2c3d4-e5f6-4a5b-9c8d-7e6f5a4b3c2d',
  'lazar@test.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYjQQBvPse2',
  NOW(),
  NOW()
) ON CONFLICT (email) DO NOTHING;

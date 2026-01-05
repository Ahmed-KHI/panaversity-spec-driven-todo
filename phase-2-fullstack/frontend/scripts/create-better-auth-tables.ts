import { Pool } from 'pg';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config({ path: '.env.local' });

async function runMigration() {
  if (!process.env.DATABASE_URL) {
    console.error('DATABASE_URL not found in environment');
    process.exit(1);
  }

  console.log('Database URL:', process.env.DATABASE_URL.substring(0, 50) + '...');
  
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
  });

  try {
    console.log('Connecting to database...');
    const client = await pool.connect();
    
    console.log('Reading SQL file...');
    const sqlPath = path.join(process.cwd(), 'better-auth-schema.sql');
    const sql = fs.readFileSync(sqlPath, 'utf-8');
    
    console.log('Executing migration...');
    await client.query(sql);
    
    console.log('✓ Better Auth tables created successfully!');
    
    client.release();
  } catch (error) {
    console.error('Migration failed:', error);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

runMigration();

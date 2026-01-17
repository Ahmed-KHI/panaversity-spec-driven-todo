import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";
import { Kysely, PostgresDialect } from "kysely";
import { Pool } from "pg";

const dialect = new PostgresDialect({
  pool: new Pool({
    connectionString: process.env.DATABASE_URL,
  })
});

const db = new Kysely<any>({
  dialect,
});

export const auth = betterAuth({
  database: {
    provider: "pg",
    db: db,
  },
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
    minPasswordLength: 8,
  },
  secret: process.env.BETTER_AUTH_SECRET || "fallback-secret-min-32-chars-long",
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
  trustedOrigins: [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://panaversity-spec-driven-todo.vercel.app",
    process.env.BETTER_AUTH_URL || "",
    process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : "",
  ].filter(Boolean),
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
  },
  plugins: [nextCookies()],
});

export type Session = typeof auth.$Infer.Session;

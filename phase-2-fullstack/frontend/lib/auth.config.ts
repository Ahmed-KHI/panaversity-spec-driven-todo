import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";

// Frontend Better Auth client - connects to backend API
// Database connection is handled by backend only
export const auth = betterAuth({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  trustedOrigins: [
    "http://localhost:3000",
    "http://127.0.0.1:3000", 
    "http://34.93.106.63",
    "https://panaversity-spec-driven-todo.vercel.app",
    process.env.BETTER_AUTH_URL || "",
    process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : "",
  ].filter(Boolean),
  plugins: [nextCookies()],
});

export type Session = typeof auth.$Infer.Session;

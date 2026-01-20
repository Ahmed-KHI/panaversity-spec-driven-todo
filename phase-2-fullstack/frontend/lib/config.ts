/**
 * Runtime configuration for API URL
 * This allows the app to work with different backend URLs without rebuilding
 */

// For client-side
export const getApiUrl = () => {
  if (typeof window !== 'undefined') {
    // Browser: use the build-time variable
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  }
  // Server-side: use runtime environment variable
  // API_URL (server-only) takes precedence over NEXT_PUBLIC_API_URL (build-time)
  return process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://todo-backend:8000'
}

export const API_URL = getApiUrl()

/**
 * Authentication utilities.
 * [Task]: T-021 (Auth Utilities)
 * [From]: spec.md §8, plan.md §8
 */

import { cookies } from 'next/headers'

export interface AuthUser {
  id: string
  email: string
  name?: string
}

export async function getAuthToken(): Promise<string | null> {
  const cookieStore = await cookies()
  return cookieStore.get('token')?.value || null
}

export async function getAuthUser(): Promise<AuthUser | null> {
  const cookieStore = await cookies()
  const userCookie = cookieStore.get('user')?.value
  
  if (!userCookie) {
    return null
  }

  try {
    return JSON.parse(userCookie)
  } catch {
    return null
  }
}

export async function setAuthCookies(token: string, user: AuthUser) {
  const cookieStore = await cookies()
  
  cookieStore.set('token', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7, // 7 days
    path: '/',
  })

  cookieStore.set('user', JSON.stringify(user), {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7, // 7 days
    path: '/',
  })
}

export async function clearAuthCookies() {
  const cookieStore = await cookies()
  cookieStore.delete('token')
  cookieStore.delete('user')
}

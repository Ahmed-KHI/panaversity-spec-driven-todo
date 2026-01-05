import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth.config'
import { cookies } from 'next/headers'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, password } = body

    // Step 1: Sign in with Better Auth (get frontend session)
    const betterAuthResult = await auth.api.signInEmail({
      body: {
        email,
        password,
      }
    })

    if (!betterAuthResult || !betterAuthResult.user) {
      return NextResponse.json(
        { error: 'Invalid credentials' },
        { status: 401 }
      )
    }

    // Step 2: Login to FastAPI backend to get JWT token
    let backendToken: string | null = null
    let backendUserId: string | null = null

    try {
      const backendResponse = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      })

      if (backendResponse.ok) {
        const backendData = await backendResponse.json()
        backendToken = backendData.access_token
        backendUserId = backendData.user.id
      } else {
        console.error('Backend login failed - user may not exist in backend yet')
      }
    } catch (backendError) {
      console.error('Failed to login to backend:', backendError)
    }

    const cookieStore = await cookies()

    // Store backend JWT token for API calls
    if (backendToken) {
      cookieStore.set('token', backendToken, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 * 7,
        path: '/',
      })
    }

    // Store user info with backend user ID
    cookieStore.set('user', JSON.stringify({
      id: backendUserId || betterAuthResult.user.id,
      email: betterAuthResult.user.email,
      name: betterAuthResult.user.name
    }), {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7,
      path: '/',
    })

    return NextResponse.json({
      success: true,
      user: {
        id: backendUserId || betterAuthResult.user.id,
        email: betterAuthResult.user.email,
        name: betterAuthResult.user.name
      }
    })
  } catch (error: any) {
    console.error('Login error:', error)
    return NextResponse.json(
      { error: error.message || 'Login failed' },
      { status: 401 }
    )
  }
}

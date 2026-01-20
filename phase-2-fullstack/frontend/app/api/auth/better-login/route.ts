import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth.config'
import { cookies } from 'next/headers'

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://todo-backend:8000'

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
      console.log(`[better-login] Attempting backend login to: ${API_URL}/api/auth/login`)
      console.log(`[better-login] Email: ${email}`)
      
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

      console.log(`[better-login] Backend response status: ${backendResponse.status}`)
      const responseText = await backendResponse.text()
      console.log(`[better-login] Backend response body: ${responseText}`)

      if (backendResponse.ok) {
        const backendData = JSON.parse(responseText)
        backendToken = backendData.access_token
        backendUserId = backendData.user.id
        console.log(`[better-login] Successfully got backend token for user: ${backendUserId}`)
      } else {
        console.error(`[better-login] Backend login failed with status ${backendResponse.status}: ${responseText}`)
      }
    } catch (backendError) {
      console.error('[better-login] Failed to login to backend:', backendError)
      console.error('[better-login] Error details:', JSON.stringify(backendError, Object.getOwnPropertyNames(backendError)))
    }

    const cookieStore = await cookies()

    // Store backend JWT token for API calls
    if (backendToken) {
      console.log('[better-login] Setting token cookie')
      cookieStore.set('token', backendToken, {
        httpOnly: true,
        secure: false, // Disabled for Kubernetes port-forward (HTTP)
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 * 7,
        path: '/',
      })
    }

    // Store user info with backend user ID
    console.log('[better-login] Setting user cookie with backend ID:', backendUserId)
    cookieStore.set('user', JSON.stringify({
      id: backendUserId || betterAuthResult.user.id,
      email: betterAuthResult.user.email,
      name: betterAuthResult.user.name
    }), {
      httpOnly: true,
      secure: false, // Disabled for Kubernetes port-forward (HTTP)
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

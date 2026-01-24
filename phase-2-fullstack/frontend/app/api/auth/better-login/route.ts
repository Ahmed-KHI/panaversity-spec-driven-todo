import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://todo-backend:8000'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, password } = body

    // Login to FastAPI backend to get JWT token
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

    if (!backendResponse.ok) {
      return NextResponse.json(
        { error: 'Invalid credentials' },
        { status: 401 }
      )
    }

    const backendData = JSON.parse(responseText)
    const backendToken = backendData.access_token
    const backendUserId = backendData.user.id
    console.log(`[better-login] Successfully got backend token for user: ${backendUserId}`)

    const cookieStore = await cookies()

    // Store backend JWT token for API calls
    if (backendToken) {
      console.log('[better-login] Setting token cookie')
      cookieStore.set('token', backendToken, {
        httpOnly: true,
        secure: false,
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 * 7,
        path: '/',
      })
    }

    // Store user info with backend user ID
    console.log('[better-login] Setting user cookie with backend ID:', backendUserId)
    cookieStore.set('user', JSON.stringify({
      id: backendUserId,
      email: backendData.user.email,
      name: backendData.user.name
    }), {
      httpOnly: true,
      secure: false,
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7,
      path: '/',
    })

    return NextResponse.json({
      success: true,
      user: {
        id: backendUserId,
        email: backendData.user.email,
        name: backendData.user.name
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

import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth.config'
import { cookies } from 'next/headers'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, password } = body

    // Sign in with Better Auth
    const result = await auth.api.signInEmail({
      body: {
        email,
        password,
      }
    })

    if (!result || !result.user || !result.token) {
      return NextResponse.json(
        { error: 'Invalid credentials' },
        { status: 401 }
      )
    }

    // Get the session to extract token
    const cookieStore = await cookies()
    const headers = new Headers()
    
    // Convert cookies to Headers format for Better Auth
    cookieStore.getAll().forEach(cookie => {
      headers.append('cookie', `${cookie.name}=${cookie.value}`)
    })

    const session = await auth.api.getSession({
      headers: headers
    })

    // Use the token from login result if session not available
    const token = session?.session?.token || result.token
    const user = session?.user || result.user

    if (!token || !user) {
      return NextResponse.json(
        { error: 'Session creation failed' },
        { status: 500 }
      )
    }

    // Store session token and user info in cookies for API calls
    cookieStore.set('token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7,
      path: '/',
    })

    cookieStore.set('user', JSON.stringify({
      id: user.id,
      email: user.email,
      name: user.name
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
        id: user.id,
        email: user.email,
        name: user.name
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

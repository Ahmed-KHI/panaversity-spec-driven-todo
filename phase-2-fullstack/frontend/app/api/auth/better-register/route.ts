import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://todo-backend:8000'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, password, name } = body

    // Register user with FastAPI backend (handles both auth and task storage)
    const backendResponse = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
      }),
    })

    if (!backendResponse.ok) {
      const errorData = await backendResponse.json().catch(() => ({ detail: 'Registration failed' }))
      return NextResponse.json(
        { error: errorData.detail || 'Registration failed' },
        { status: backendResponse.status }
      )
    }

    const data = await backendResponse.json()
    
    return NextResponse.json({
      user: {
        id: data.id,
        email: data.email,
        name: name || email.split('@')[0],
      },
      message: data.message || 'Registration successful'
    })
  } catch (error) {
    console.error('Registration error:', error)
    return NextResponse.json(
      { error: 'Internal server error during registration' },
      { status: 500 }
    )
  }
}

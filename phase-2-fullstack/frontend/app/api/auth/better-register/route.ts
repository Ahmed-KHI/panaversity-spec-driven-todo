import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth.config'
import { cookies } from 'next/headers'

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://todo-backend:8000'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, password, name } = body

    // Step 1: Register user with Better Auth (frontend authentication)
    const betterAuthResult = await auth.api.signUpEmail({
      body: {
        email,
        password,
        name: name || email.split('@')[0],
      }
    })

    if (!betterAuthResult || !betterAuthResult.user) {
      return NextResponse.json(
        { error: 'Registration failed' },
        { status: 400 }
      )
    }

    // Step 2: Register user with FastAPI backend (task storage)
    try {
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
        // If backend registration fails but user already exists, that's OK
        const errorData = await backendResponse.json().catch(() => ({}))
        if (backendResponse.status !== 400 || !errorData.detail?.includes('already registered')) {
          console.error('Backend registration failed:', errorData)
        }
      } else {
        const backendData = await backendResponse.json()
        console.log('Backend user created:', backendData)
      }
    } catch (backendError) {
      console.error('Failed to register with backend:', backendError)
      // Continue - Better Auth user is created, backend registration can fail
    }

    return NextResponse.json(
      { 
        success: true,
        message: 'Account created successfully',
        user: betterAuthResult.user
      },
      { status: 201 }
    )
  } catch (error: any) {
    console.error('Registration error:', error)
    return NextResponse.json(
      { error: error.message || 'Registration failed' },
      { status: 400 }
    )
  }
}

import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth.config'
import { cookies } from 'next/headers'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, password, name } = body

    // Register user with Better Auth
    const result = await auth.api.signUpEmail({
      body: {
        email,
        password,
        name: name || email.split('@')[0],
      }
    })

    if (!result || !result.user) {
      return NextResponse.json(
        { error: 'Registration failed' },
        { status: 400 }
      )
    }

    return NextResponse.json(
      { 
        success: true,
        message: 'Account created successfully',
        user: result.user
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

import { NextRequest, NextResponse } from 'next/server'
import { apiClient } from '@/lib/api'
import { cookies } from 'next/headers'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const result = await apiClient.login(body)
    
    // Set HTTP-only cookies
    const cookieStore = await cookies()
    
    cookieStore.set('token', result.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: '/',
    })

    cookieStore.set('user', JSON.stringify(result.user), {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7,
      path: '/',
    })

    return NextResponse.json({ success: true, user: result.user })
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Login failed' },
      { status: 401 }
    )
  }
}

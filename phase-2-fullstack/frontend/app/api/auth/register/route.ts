import { NextRequest, NextResponse } from 'next/server'
import { apiClient } from '@/lib/api'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const result = await apiClient.register(body)
    
    return NextResponse.json(result, { status: 201 })
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Registration failed' },
      { status: 400 }
    )
  }
}

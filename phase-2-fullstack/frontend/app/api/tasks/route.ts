import { NextRequest, NextResponse } from 'next/server'
import { getAuthToken } from '@/lib/auth'
import { apiClient } from '@/lib/api'

export async function POST(request: NextRequest) {
  const token = await getAuthToken()
  
  if (!token) {
    return NextResponse.json({ error: 'Not authenticated' }, { status: 401 })
  }

  try {
    const body = await request.json()
    const { userId, title, description } = body

    apiClient.setToken(token)
    const task = await apiClient.createTask(userId, { title, description })

    return NextResponse.json(task, { status: 201 })
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to create task' },
      { status: 400 }
    )
  }
}

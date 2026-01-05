import { NextRequest, NextResponse } from 'next/server'
import { getAuthToken } from '@/lib/auth'
import { apiClient } from '@/lib/api'

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const token = await getAuthToken()
  
  if (!token) {
    return NextResponse.json({ error: 'Not authenticated' }, { status: 401 })
  }

  try {
    const { id } = await params
    const body = await request.json()
    const { userId, completed } = body

    apiClient.setToken(token)
    const task = await apiClient.toggleTask(userId, parseInt(id), completed)

    return NextResponse.json(task)
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to toggle task' },
      { status: 400 }
    )
  }
}

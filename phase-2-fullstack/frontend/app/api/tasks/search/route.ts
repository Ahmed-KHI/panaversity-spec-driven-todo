import { NextRequest, NextResponse } from 'next/server'
import { getAuthToken } from '@/lib/auth'
import { getApiUrl } from '@/lib/config'

export async function POST(request: NextRequest) {
  try {
    const token = await getAuthToken()
    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { userId } = await request.json()
    if (!userId) {
      return NextResponse.json({ error: 'userId is required' }, { status: 400 })
    }

    // Get query params from URL
    const searchParams = request.nextUrl.searchParams
    const apiUrl = getApiUrl()

    // Build backend API URL with query params
    const backendUrl = new URL(`/api/${userId}/tasks`, apiUrl)
    
    // Copy all search params to backend request
    searchParams.forEach((value, key) => {
      backendUrl.searchParams.append(key, value)
    })

    // Call backend with authentication
    const response = await fetch(backendUrl.toString(), {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const error = await response.text()
      console.error('Backend search error:', error)
      return NextResponse.json(
        { error: 'Failed to search tasks' },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error: any) {
    console.error('Search API error:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}

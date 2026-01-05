import { NextResponse } from 'next/server'
import { auth } from '@/lib/auth.config'
import { cookies } from 'next/headers'

export async function POST() {
  const cookieStore = await cookies()
  
  try {
    // Convert cookies to Headers for Better Auth
    const headers = new Headers()
    cookieStore.getAll().forEach(cookie => {
      headers.append('cookie', `${cookie.name}=${cookie.value}`)
    })
    
    // Sign out with Better Auth
    await auth.api.signOut({ headers })
  } catch (error) {
    console.error('Better Auth logout error:', error)
  }

  // Clear our custom cookies
  cookieStore.delete('token')
  cookieStore.delete('user')
  
  return NextResponse.json({ success: true })
}

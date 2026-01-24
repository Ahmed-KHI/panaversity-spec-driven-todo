import { redirect } from 'next/navigation'
import { apiClient } from '@/lib/api'
import TaskList from '@/components/TaskList'
import Header from '@/components/Header'
import Link from 'next/link'
import { cookies } from 'next/headers'

export default async function DashboardPage() {
  try {
    // Check authentication via backend cookies (no Better Auth session needed)
    const cookieStore = await cookies()
    const backendToken = cookieStore.get('token')?.value
    const backendUserCookie = cookieStore.get('user')?.value
    
    if (!backendToken || !backendUserCookie) {
      redirect('/login')
    }

    // Parse backend user
    let user: any
    try {
      user = JSON.parse(backendUserCookie)
    } catch (e) {
      console.error('Failed to parse backend user cookie:', e)
      redirect('/login')
    }

    // Validate user has proper ID
    if (!user.id || user.id.length < 10) {
      console.error('Invalid user ID detected:', user.id)
      redirect('/login')
    }

    const backendUserId = user.id

    if (backendToken) {
      apiClient.setToken(backendToken)
    }
    
    let tasks: any[] = []
    try {
      const response = await apiClient.getTasks(backendUserId)
      tasks = response.tasks
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
      // Continue with empty tasks array
    }

    return (
      <div className="min-h-screen bg-gray-50">
        <Header user={user} />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">My Tasks</h1>
              <p className="mt-2 text-gray-600">
                Manage your tasks efficiently
              </p>
            </div>
            
            <Link
              href="/chat"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
            >
              💬 Chat with AI Assistant
            </Link>
          </div>

          <TaskList initialTasks={tasks} userId={backendUserId} />
        </main>
      </div>
    )
  } catch (error) {
    console.error('Dashboard error:', error)
    redirect('/login')
  }
}

import { redirect } from 'next/navigation'
import { auth } from '@/lib/auth.config'
import { apiClient } from '@/lib/api'
import TaskList from '@/components/TaskList'
import Header from '@/components/Header'
import Link from 'next/link'

export default async function DashboardPage() {
  try {
    // Use Better Auth session instead of custom cookies
    const session = await auth.api.getSession({
      headers: await import('next/headers').then(m => m.headers())
    })

    if (!session?.user) {
      redirect('/login')
    }

    const user = session.user

    // Validate user has proper ID
    if (!user.id || user.id.length < 10) {
      console.error('Invalid user ID detected:', user.id)
      redirect('/login')
    }

    // Get backend token and user info from custom cookies for API calls
    const { cookies } = await import('next/headers')
    const cookieStore = await cookies()
    const backendToken = cookieStore.get('token')?.value
    const backendUserCookie = cookieStore.get('user')?.value
    
    // Parse backend user to get the backend UUID
    let backendUserId = user.id // fallback to session user id
    if (backendUserCookie) {
      try {
        const backendUser = JSON.parse(backendUserCookie)
        backendUserId = backendUser.id
      } catch (e) {
        console.error('Failed to parse backend user cookie:', e)
      }
    }

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

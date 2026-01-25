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
      <div className="min-h-screen">
        <Header user={user} />
        
        <main className="max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-6 md:py-8">
          <div className="mb-6 sm:mb-8 glass p-5 sm:p-6 md:p-8 rounded-2xl sm:rounded-3xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 sm:gap-6 shadow-xl hover:shadow-2xl transition-all">
            <div className="w-full sm:w-auto">
              <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                ✨ My Tasks
              </h1>
              <p className="mt-2 sm:mt-3 text-gray-600 font-medium text-sm sm:text-base md:text-lg">
                Manage your tasks efficiently with premium features
              </p>
            </div>
            
            <Link
              href="/chat"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3 sm:py-3.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl hover:scale-105 font-bold text-sm sm:text-base whitespace-nowrap"
            >
              💬 Chat with AI
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

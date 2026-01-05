import { redirect } from 'next/navigation'
import { getAuthToken, getAuthUser } from '@/lib/auth'
import { apiClient } from '@/lib/api'
import TaskList from '@/components/TaskList'
import Header from '@/components/Header'

export default async function DashboardPage() {
  const token = await getAuthToken()
  const user = await getAuthUser()

  if (!token || !user) {
    redirect('/login')
  }

  apiClient.setToken(token)
  const { tasks } = await apiClient.getTasks(user.id)

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Tasks</h1>
          <p className="mt-2 text-gray-600">
            Manage your tasks efficiently
          </p>
        </div>

        <TaskList initialTasks={tasks} userId={user.id} />
      </main>
    </div>
  )
}

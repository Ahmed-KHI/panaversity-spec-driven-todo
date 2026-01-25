'use client'

import { useState, useEffect } from 'react'
import { Task } from '@/lib/api'
import TaskItem from './TaskItem'
import TaskForm from './TaskForm'
import AdvancedSearch, { SearchFilters } from './AdvancedSearch'

interface TaskListProps {
  initialTasks: Task[]
  userId: string
}

export default function TaskList({ initialTasks, userId }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks)
  const [displayedTasks, setDisplayedTasks] = useState<Task[]>(initialTasks)
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all')
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [activeFilters, setActiveFilters] = useState<SearchFilters>({})
  const [isAdvancedSearch, setIsAdvancedSearch] = useState(false)

  // Apply local filtering
  useEffect(() => {
    let filtered = [...tasks]

    // Only apply local filters if NOT in advanced search mode
    // (advanced search filters are already applied by backend)
    if (!isAdvancedSearch) {
      // Apply status filter
      if (filter === 'pending') {
        filtered = filtered.filter(t => !t.completed)
      } else if (filter === 'completed') {
        filtered = filtered.filter(t => t.completed)
      }
    }

    setDisplayedTasks(filtered)
  }, [tasks, filter, isAdvancedSearch])

  const handleAdvancedSearch = async (filters: SearchFilters) => {
    setLoading(true)
    setIsAdvancedSearch(true)
    
    // Store filters for display purposes
    setActiveFilters(filters)
    
    // Build query params for backend
    const params = new URLSearchParams()
    
    if (filters.search) params.append('search', filters.search)
    if (filters.priority?.length) {
      filters.priority.forEach(p => params.append('priority', p))
    }
    if (filters.tags?.length) {
      filters.tags.forEach(t => params.append('tags', t))
    }
    if (filters.dueBefore) params.append('due_before', filters.dueBefore)
    if (filters.dueAfter) params.append('due_after', filters.dueAfter)
    if (filters.isRecurring !== undefined) {
      params.append('is_recurring', String(filters.isRecurring))
    }
    if (filters.status && filters.status !== 'all') {
      params.append('completed', filters.status)
    }

    try {
      const response = await fetch(`/api/tasks/search?${params.toString()}`, {
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId }),
        method: 'POST'
      })

      if (response.ok) {
        const data = await response.json()
        // Backend returns already filtered tasks, so we just set them
        setTasks(data.tasks)
      } else {
        console.error('Advanced search failed with status:', response.status)
      }
    } catch (error) {
      console.error('Advanced search failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleResetSearch = () => {
    setActiveFilters({})
    setIsAdvancedSearch(false)
    setTasks(initialTasks)
  }

  const handleTaskCreated = (newTask: Task) => {
    setTasks([newTask, ...tasks])
    setShowForm(false)
  }

  const handleTaskUpdated = (updatedTask: Task) => {
    setTasks(tasks.map((t) => (t.id === updatedTask.id ? updatedTask : t)))
  }

  const handleTaskDeleted = (taskId: number) => {
    setTasks(tasks.filter((t) => t.id !== taskId))
  }

  const pendingCount = tasks.filter((t) => !t.completed).length
  const completedCount = tasks.filter((t) => t.completed).length

  return (
    <div className="space-y-6">
      {/* Advanced Search Component */}
      <AdvancedSearch onSearch={handleAdvancedSearch} onReset={handleResetSearch} />

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
        <div className="glass p-5 sm:p-6 rounded-xl sm:rounded-2xl hover:scale-105 transition-transform cursor-pointer group">
          <p className="text-xs sm:text-sm font-medium text-gray-600 uppercase tracking-wide">Total Tasks</p>
          <p className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent group-hover:scale-110 transition-transform mt-1">{tasks.length}</p>
        </div>
        <div className="glass p-5 sm:p-6 rounded-xl sm:rounded-2xl hover:scale-105 transition-transform cursor-pointer group">
          <p className="text-xs sm:text-sm font-medium text-gray-600 uppercase tracking-wide">Pending</p>
          <p className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-yellow-500 to-orange-600 bg-clip-text text-transparent group-hover:scale-110 transition-transform mt-1">{pendingCount}</p>
        </div>
        <div className="glass p-5 sm:p-6 rounded-xl sm:rounded-2xl hover:scale-105 transition-transform cursor-pointer group sm:col-span-2 lg:col-span-1">
          <p className="text-xs sm:text-sm font-medium text-gray-600 uppercase tracking-wide">Completed</p>
          <p className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-green-500 to-emerald-600 bg-clip-text text-transparent group-hover:scale-110 transition-transform mt-1">{completedCount}</p>
        </div>
      </div>

      {/* Filter and Add Button */}
      <div className="flex flex-col gap-4 glass p-4 sm:p-5 rounded-xl sm:rounded-2xl">
        <div className="flex flex-wrap gap-2 sm:gap-3">
          <button
            onClick={() => setFilter('all')}
            className={`flex-1 min-w-[80px] px-4 sm:px-5 py-2 sm:py-2.5 rounded-lg sm:rounded-xl text-xs sm:text-sm font-medium transition-all hover:scale-105 ${
              filter === 'all'
                ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg'
                : 'bg-white/60 text-gray-700 hover:bg-white/80 border border-white/40'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('pending')}
            className={`flex-1 min-w-[80px] px-4 sm:px-5 py-2 sm:py-2.5 rounded-lg sm:rounded-xl text-xs sm:text-sm font-medium transition-all hover:scale-105 ${
              filter === 'pending'
                ? 'bg-gradient-to-r from-yellow-500 to-orange-600 text-white shadow-lg'
                : 'bg-white/60 text-gray-700 hover:bg-white/80 border border-white/40'
            }`}
          >
            Pending
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`flex-1 min-w-[80px] px-4 sm:px-5 py-2 sm:py-2.5 rounded-lg sm:rounded-xl text-xs sm:text-sm font-medium transition-all hover:scale-105 ${
              filter === 'completed'
                ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg'
                : 'bg-white/60 text-gray-700 hover:bg-white/80 border border-white/40'
            }`}
          >
            Completed
          </button>
        </div>

        <button
          onClick={() => setShowForm(!showForm)}
          className="w-full px-5 sm:px-6 py-2.5 sm:py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg sm:rounded-xl hover:from-indigo-700 hover:to-purple-700 text-sm sm:text-base font-medium shadow-lg hover:shadow-xl hover:scale-105 transition-all"
        >
          {showForm ? '✕ Cancel' : '✨ New Task'}
        </button>
      </div>

      {/* Task Form */}
      {showForm && (
        <div className="glass p-6 rounded-2xl">
          <h3 className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-4">✨ Create New Task</h3>
          <TaskForm userId={userId} onTaskCreated={handleTaskCreated} />
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="glass border border-indigo-200 rounded-2xl p-5 text-center">
          <div className="flex items-center justify-center gap-3">
            <div className="animate-spin h-5 w-5 border-2 border-indigo-600 border-t-transparent rounded-full"></div>
            <p className="text-indigo-700 font-medium">🔍 Searching tasks...</p>
          </div>
        </div>
      )}

      {/* Task List */}
      <div className="space-y-3">
        {displayedTasks.length === 0 ? (
          <div className="glass p-10 rounded-2xl text-center">
            <div className="text-6xl mb-4">📋</div>
            <p className="text-gray-600 font-medium text-lg">
              {filter === 'all' && 'No tasks found. Try adjusting your filters or create a new task!'}
              {filter === 'pending' && 'No pending tasks found. Great job! 🎉'}
              {filter === 'completed' && 'No completed tasks found yet. Keep going! 🚀'}
            </p>
          </div>
        ) : (
          displayedTasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              userId={userId}
              onTaskUpdated={handleTaskUpdated}
              onTaskDeleted={handleTaskDeleted}
            />
          ))
        )}
      </div>

      {/* Results Summary */}
      {Object.keys(activeFilters).length > 0 && (
        <div className="glass border border-indigo-200 rounded-2xl p-4">
          <p className="text-sm font-medium bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            Showing <span className="font-bold text-lg">{displayedTasks.length}</span> of <span className="font-bold text-lg">{tasks.length}</span> total tasks
          </p>
        </div>
      )}
    </div>
  )
}

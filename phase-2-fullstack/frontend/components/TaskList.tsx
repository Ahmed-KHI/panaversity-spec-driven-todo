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

  // Apply local filtering
  useEffect(() => {
    let filtered = [...tasks]

    // Apply status filter
    if (filter === 'pending') {
      filtered = filtered.filter(t => !t.completed)
    } else if (filter === 'completed') {
      filtered = filtered.filter(t => t.completed)
    }

    // Apply active search filters
    if (activeFilters.search) {
      const searchLower = activeFilters.search.toLowerCase()
      filtered = filtered.filter(t => 
        t.title.toLowerCase().includes(searchLower) ||
        (t.description?.toLowerCase().includes(searchLower))
      )
    }

    if (activeFilters.priority?.length) {
      filtered = filtered.filter(t => 
        activeFilters.priority?.includes((t as any).priority)
      )
    }

    if (activeFilters.isRecurring !== undefined) {
      filtered = filtered.filter(t => 
        (t as any).is_recurring === activeFilters.isRecurring
      )
    }

    if (activeFilters.dueAfter) {
      const after = new Date(activeFilters.dueAfter)
      filtered = filtered.filter(t => 
        (t as any).due_date && new Date((t as any).due_date) >= after
      )
    }

    if (activeFilters.dueBefore) {
      const before = new Date(activeFilters.dueBefore)
      filtered = filtered.filter(t => 
        (t as any).due_date && new Date((t as any).due_date) <= before
      )
    }

    if (activeFilters.tags?.length) {
      filtered = filtered.filter(t => {
        const taskTags = ((t as any).tags || []).map((tag: any) => tag.name)
        return activeFilters.tags?.every(tag => taskTags.includes(tag))
      })
    }

    setDisplayedTasks(filtered)
  }, [tasks, filter, activeFilters])

  const handleAdvancedSearch = async (filters: SearchFilters) => {
    setLoading(true)
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
        setTasks(data.tasks)
      }
    } catch (error) {
      console.error('Advanced search failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleResetSearch = () => {
    setActiveFilters({})
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
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="text-sm font-medium text-gray-600">Total Tasks</p>
          <p className="text-3xl font-bold text-gray-900">{tasks.length}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="text-sm font-medium text-gray-600">Pending</p>
          <p className="text-3xl font-bold text-yellow-600">{pendingCount}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="text-sm font-medium text-gray-600">Completed</p>
          <p className="text-3xl font-bold text-green-600">{completedCount}</p>
        </div>
      </div>

      {/* Filter and Add Button */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-4 rounded-lg shadow">
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              filter === 'all'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('pending')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              filter === 'pending'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Pending
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              filter === 'completed'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Completed
          </button>
        </div>

        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm font-medium shadow-md"
        >
          {showForm ? 'Cancel' : '+ New Task'}
        </button>
      </div>

      {/* Task Form */}
      {showForm && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Task</h3>
          <TaskForm userId={userId} onTaskCreated={handleTaskCreated} />
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
          <p className="text-blue-700">🔍 Searching tasks...</p>
        </div>
      )}

      {/* Task List */}
      <div className="space-y-3">
        {displayedTasks.length === 0 ? (
          <div className="bg-white p-8 rounded-lg shadow text-center">
            <p className="text-gray-500">
              {filter === 'all' && 'No tasks found. Try adjusting your filters or create a new task!'}
              {filter === 'pending' && 'No pending tasks found. Great job!'}
              {filter === 'completed' && 'No completed tasks found yet.'}
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
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <p className="text-sm text-gray-600">
            Showing <span className="font-semibold">{displayedTasks.length}</span> of <span className="font-semibold">{tasks.length}</span> total tasks
          </p>
        </div>
      )}
    </div>
  )
}

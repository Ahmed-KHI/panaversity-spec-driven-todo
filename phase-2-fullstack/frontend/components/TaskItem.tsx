'use client'

import { useState } from 'react'
import { Task, apiClient } from '@/lib/api'

interface TaskItemProps {
  task: Task
  userId: string
  onTaskUpdated: (task: Task) => void
  onTaskDeleted: (taskId: number) => void
}

export default function TaskItem({ task, userId, onTaskUpdated, onTaskDeleted }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [title, setTitle] = useState(task.title)
  const [description, setDescription] = useState(task.description || '')
  const [priority, setPriority] = useState((task as any).priority || 'medium')
  const [dueDate, setDueDate] = useState((task as any).due_date ? new Date((task as any).due_date).toISOString().slice(0, 16) : '')
  const [isRecurring, setIsRecurring] = useState((task as any).is_recurring || false)
  const [recurrenceFrequency, setRecurrenceFrequency] = useState(
    (task as any).recurrence_pattern?.frequency || 'daily'
  )
  const [tags, setTags] = useState(
    (task as any).tags ? (task as any).tags.map((t: any) => t.name).join(', ') : ''
  )
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleToggle = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/tasks/${task.id}/toggle`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId, completed: !task.completed }),
      })

      if (!response.ok) throw new Error('Failed to toggle task')

      const updatedTask = await response.json()
      onTaskUpdated(updatedTask)
    } catch (error) {
      console.error('Failed to toggle task:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    
    try {
      const payload: any = { 
        userId, 
        title, 
        description,
        priority,
        due_date: dueDate || null,
        is_recurring: isRecurring,
        recurrence_pattern: isRecurring ? {
          frequency: recurrenceFrequency,
          interval: 1
        } : undefined
      }

      // Add tags if provided (comma-separated)
      if (tags.trim()) {
        payload.tags = tags.split(',').map((t: string) => t.trim()).filter((t: string) => t.length > 0)
      }

      console.log('Updating task:', payload)

      const response = await fetch(`/api/tasks/${task.id}`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Important for auth cookies
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
        throw new Error(errorData.error || `Failed to update task: ${response.status}`)
      }

      const updatedTask = await response.json()
      console.log('Task updated successfully:', updatedTask)
      onTaskUpdated(updatedTask)
      setIsEditing(false)
    } catch (error: any) {
      console.error('Failed to update task:', error)
      setError(error.message || 'Failed to update task. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this task?')) return

    setLoading(true)
    try {
      const response = await fetch(`/api/tasks/${task.id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId }),
      })

      if (!response.ok) throw new Error('Failed to delete task')

      onTaskDeleted(task.id)
    } catch (error) {
      console.error('Failed to delete task:', error)
    } finally {
      setLoading(false)
    }
  }

  if (isEditing) {
    return (
      <div className="glass p-6 rounded-2xl hover:shadow-xl transition-all">
        <form onSubmit={handleUpdate} className="space-y-4">
          {/* Error Display */}
          {error && (
            <div className="p-4 bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-xl flex items-start gap-2 shadow-sm">
              <span className="text-red-600 font-bold text-lg">⚠️</span>
              <div className="flex-1">
                <p className="text-sm font-medium text-red-800">Update Failed</p>
                <p className="text-sm text-red-700">{error}</p>
              </div>
              <button
                type="button"
                onClick={() => setError(null)}
                className="text-red-400 hover:text-red-600"
              >
                ✕
              </button>
            </div>
          )}

          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900"
            placeholder="Task title"
            required
          />
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900"
            placeholder="Description (optional)"
            rows={3}
          />
          
          {/* Priority Dropdown */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>

          {/* Due Date Picker */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
            <input
              type="datetime-local"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900"
            />
          </div>

          {/* Tags Field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900"
              placeholder="work, urgent, personal (comma-separated)"
            />
            <p className="mt-1 text-xs text-gray-500">
              Separate multiple tags with commas
            </p>
          </div>

          {/* Recurring Checkbox */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="edit-recurring"
              checked={isRecurring}
              onChange={(e) => setIsRecurring(e.target.checked)}
              className="h-4 w-4 text-primary-600 rounded"
            />
            <label htmlFor="edit-recurring" className="text-sm font-medium text-gray-700">
              Recurring Task
            </label>
          </div>

          {/* Recurrence Frequency (conditional) */}
          {isRecurring && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Frequency</label>
              <select
                value={recurrenceFrequency}
                onChange={(e) => setRecurrenceFrequency(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 shadow-lg hover:shadow-xl hover:scale-105 transition-all font-medium"
            >
              {loading ? '🔄 Saving...' : '✔️ Save'}
            </button>
            <button
              type="button"
              onClick={() => setIsEditing(false)}
              className="px-6 py-3 bg-white/60 text-gray-700 rounded-xl hover:bg-white/80 border border-white/40 hover:scale-105 transition-all font-medium"
            >
              ✕ Cancel
            </button>
          </div>
        </form>
      </div>
    )
  }

  return (
    <div className={`glass p-4 sm:p-5 rounded-xl sm:rounded-2xl hover:shadow-xl transition-all hover:scale-[1.02] ${
      task.completed ? 'opacity-75' : ''
    }`}>
      <div className="flex items-start gap-3 sm:gap-4">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={handleToggle}
          disabled={loading}
          className="mt-1 h-5 w-5 sm:h-6 sm:w-6 text-indigo-600 rounded-lg focus:ring-2 focus:ring-indigo-500 cursor-pointer hover:scale-110 transition-transform flex-shrink-0"
        />
        
        <div className="flex-1 min-w-0">
          <div className="flex items-start sm:items-center gap-2 flex-wrap mb-2">
            <h3 className={`text-base sm:text-lg font-bold break-words ${
              task.completed ? 'line-through text-gray-500' : 'bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent'
            }`}>
              {task.title}
            </h3>
            
            {/* Priority Badge */}
            {(task as any).priority && (
              <span className={`px-2 sm:px-3 py-1 sm:py-1.5 text-[10px] sm:text-xs font-bold rounded-lg sm:rounded-xl shadow-md whitespace-nowrap ${
                (task as any).priority === 'urgent' ? 'bg-gradient-to-r from-red-500 to-pink-600 text-white' :
                (task as any).priority === 'high' ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white' :
                (task as any).priority === 'medium' ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-white' :
                'bg-gradient-to-r from-green-400 to-emerald-500 text-white'
              }`}>
                {((task as any).priority as string).toUpperCase()}
              </span>
            )}

            {/* Recurring Badge */}
            {(task as any).is_recurring && (
              <span className="px-2 sm:px-3 py-1 sm:py-1.5 text-[10px] sm:text-xs font-bold rounded-lg sm:rounded-xl bg-gradient-to-r from-purple-500 to-indigo-600 text-white shadow-md whitespace-nowrap">
                🔄 RECURRING
              </span>
            )}

            {/* Tags Display */}
            {(task as any).tags && (task as any).tags.length > 0 && (
              <div className="flex gap-1 flex-wrap w-full sm:w-auto">
                {(task as any).tags.map((tag: any, index: number) => (
                  <span key={index} className="px-2 py-1 text-[10px] sm:text-xs font-semibold rounded-md sm:rounded-lg bg-gradient-to-r from-cyan-400 to-blue-500 text-white shadow-sm">
                    #{tag.name}
                  </span>
                ))}
              </div>
            )}
          </div>

          {task.description && (
            <p className="mt-2 text-xs sm:text-sm text-gray-700 leading-relaxed break-words">{task.description}</p>
          )}

          {/* Due Date */}
          {(task as any).due_date && (
            <p className="mt-2 sm:mt-3 text-[10px] sm:text-xs font-medium text-indigo-600 flex items-center gap-1">
              📅 Due: {new Date((task as any).due_date).toLocaleString()}
            </p>
          )}

          <p className="mt-2 text-[10px] sm:text-xs text-gray-500 flex items-center gap-1">
            🕒 Created: {new Date(task.created_at).toLocaleDateString()}
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-2 flex-shrink-0">
          <button
            onClick={() => setIsEditing(true)}
            disabled={loading}
            className="px-3 sm:px-4 py-1.5 sm:py-2 text-xs sm:text-sm font-medium bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg sm:rounded-xl hover:from-blue-600 hover:to-indigo-700 disabled:opacity-50 shadow-md hover:shadow-lg hover:scale-105 transition-all whitespace-nowrap"
          >
            ✏️ <span className="hidden sm:inline">Edit</span>
          </button>
          <button
            onClick={handleDelete}
            disabled={loading}
            className="px-3 sm:px-4 py-1.5 sm:py-2 text-xs sm:text-sm font-medium bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-lg sm:rounded-xl hover:from-red-600 hover:to-pink-700 disabled:opacity-50 shadow-md hover:shadow-lg hover:scale-105 transition-all whitespace-nowrap"
          >
            🗑️ <span className="hidden sm:inline">Delete</span>
          </button>
        </div>
      </div>
    </div>
  )
}

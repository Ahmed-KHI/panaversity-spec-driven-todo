'use client'

import { useState } from 'react'
import { Task } from '@/lib/api'
import TaskItem from './TaskItem'
import TaskForm from './TaskForm'

interface TaskListProps {
  initialTasks: Task[]
  userId: string
}

export default function TaskList({ initialTasks, userId }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks)
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all')
  const [showForm, setShowForm] = useState(false)

  const filteredTasks = tasks.filter((task) => {
    if (filter === 'pending') return !task.completed
    if (filter === 'completed') return task.completed
    return true
  })

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
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('pending')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              filter === 'pending'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Pending
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              filter === 'completed'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Completed
          </button>
        </div>

        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 text-sm font-medium"
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

      {/* Task List */}
      <div className="space-y-3">
        {filteredTasks.length === 0 ? (
          <div className="bg-white p-8 rounded-lg shadow text-center">
            <p className="text-gray-500">
              {filter === 'all' && 'No tasks yet. Create one to get started!'}
              {filter === 'pending' && 'No pending tasks. Great job!'}
              {filter === 'completed' && 'No completed tasks yet.'}
            </p>
          </div>
        ) : (
          filteredTasks.map((task) => (
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
    </div>
  )
}

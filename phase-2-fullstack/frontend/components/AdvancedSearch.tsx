'use client'

import { useState } from 'react'

interface AdvancedSearchProps {
  onSearch: (filters: SearchFilters) => void
  onReset: () => void
}

export interface SearchFilters {
  search?: string
  priority?: string[]
  tags?: string[]
  status?: 'all' | 'pending' | 'completed'
  dueBefore?: string
  dueAfter?: string
  isRecurring?: boolean
}

export default function AdvancedSearch({ onSearch, onReset }: AdvancedSearchProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [filters, setFilters] = useState<SearchFilters>({
    status: 'all'
  })

  const handleSearch = () => {
    onSearch(filters)
  }

  const handleReset = () => {
    setFilters({ status: 'all' })
    onReset()
  }

  return (
    <div className="bg-white p-4 rounded-lg shadow mb-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">🔍 Advanced Search & Filters</h3>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-blue-600 hover:text-blue-800 font-medium text-sm"
        >
          {isExpanded ? '▲ Hide' : '▼ Show'}
        </button>
      </div>

      {isExpanded && (
        <div className="mt-4 space-y-4">
          {/* Search Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search (Title/Description)
            </label>
            <input
              type="text"
              placeholder="Search tasks..."
              value={filters.search || ''}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value as any })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900"
              >
                <option value="all">All Tasks</option>
                <option value="pending">Pending</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            {/* Priority Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority
              </label>
              <select
                multiple
                value={filters.priority || []}
                onChange={(e) => {
                  const selected = Array.from(e.target.selectedOptions, option => option.value)
                  setFilters({ ...filters, priority: selected })
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900"
                size={4}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">Hold Ctrl/Cmd to select multiple</p>
            </div>

            {/* Recurring Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Task Type
              </label>
              <select
                value={filters.isRecurring === undefined ? 'all' : filters.isRecurring ? 'recurring' : 'one-time'}
                onChange={(e) => {
                  const value = e.target.value
                  setFilters({ 
                    ...filters, 
                    isRecurring: value === 'all' ? undefined : value === 'recurring'
                  })
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900"
              >
                <option value="all">All Tasks</option>
                <option value="recurring">Recurring Only</option>
                <option value="one-time">One-time Only</option>
              </select>
            </div>
          </div>

          {/* Date Range */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Due After
              </label>
              <input
                type="datetime-local"
                value={filters.dueAfter || ''}
                onChange={(e) => setFilters({ ...filters, dueAfter: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Due Before
              </label>
              <input
                type="datetime-local"
                value={filters.dueBefore || ''}
                onChange={(e) => setFilters({ ...filters, dueBefore: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900"
              />
            </div>
          </div>

          {/* Tags Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tags (comma-separated)
            </label>
            <input
              type="text"
              placeholder="work, urgent, personal"
              value={filters.tags?.join(', ') || ''}
              onChange={(e) => {
                const tags = e.target.value
                  .split(',')
                  .map(t => t.trim())
                  .filter(t => t.length > 0)
                setFilters({ ...filters, tags: tags.length > 0 ? tags : undefined })
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900"
            />
            <p className="text-xs text-gray-500 mt-1">Separate multiple tags with commas</p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 pt-2">
            <button
              onClick={handleSearch}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium shadow-md"
            >
              🔍 Apply Filters
            </button>
            <button
              onClick={handleReset}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 font-medium"
            >
              Clear All
            </button>
          </div>

          {/* Active Filters Summary */}
          {(filters.search || filters.priority?.length || filters.tags?.length || 
            filters.dueAfter || filters.dueBefore || filters.isRecurring !== undefined) && (
            <div className="pt-3 border-t">
              <p className="text-sm font-medium text-gray-700 mb-2">Active Filters:</p>
              <div className="flex flex-wrap gap-2">
                {filters.search && (
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                    Search: "{filters.search}"
                  </span>
                )}
                {filters.priority?.map(p => (
                  <span key={p} className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                    Priority: {p}
                  </span>
                ))}
                {filters.tags?.map(t => (
                  <span key={t} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                    Tag: {t}
                  </span>
                ))}
                {filters.isRecurring !== undefined && (
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                    {filters.isRecurring ? 'Recurring' : 'One-time'}
                  </span>
                )}
                {(filters.dueAfter || filters.dueBefore) && (
                  <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full">
                    Date Range Set
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

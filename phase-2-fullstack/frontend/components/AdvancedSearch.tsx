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

  // Count active filters
  const activeFilterCount = [
    filters.search,
    filters.priority?.length,
    filters.tags?.length,
    filters.status !== 'all',
    filters.dueAfter,
    filters.dueBefore,
    filters.isRecurring !== undefined
  ].filter(Boolean).length

  return (
    <div className="bg-gradient-to-r from-blue-50 via-purple-50 to-pink-50 p-5 rounded-xl shadow-lg mb-6 border border-blue-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg shadow-md">
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <div>
            <h3 className="text-xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              Advanced Search & Filters
            </h3>
            {activeFilterCount > 0 && (
              <p className="text-xs text-gray-600 font-medium">
                {activeFilterCount} filter{activeFilterCount > 1 ? 's' : ''} active
              </p>
            )}
          </div>
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 px-4 py-2 bg-white border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-600 hover:text-white font-semibold text-sm transition-all duration-200 shadow-md hover:shadow-lg"
        >
          {isExpanded ? (
            <>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
              Hide Filters
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
              Show Filters
            </>
          )}
        </button>
      </div>

      {isExpanded && (
        <div className="mt-5 space-y-5 bg-white p-5 rounded-lg shadow-inner">
          {/* Search Input */}
          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
              <svg className="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Search (Title/Description)
            </label>
            <div className="relative">
              <input
                type="text"
                placeholder="Search tasks by title or description..."
                value={filters.search || ''}
                onChange={(e) => setFilters({ ...filters, search: e.target.value || undefined })}
                className="w-full pl-10 pr-3 py-3 border-2 border-gray-300 rounded-lg text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
              />
              <svg className="absolute left-3 top-3.5 w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Status Filter */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
                <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Status
              </label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value as any })}
                className="w-full px-3 py-3 border-2 border-gray-300 rounded-lg text-gray-900 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all font-medium"
              >
                <option value="all">📋 All Tasks</option>
                <option value="pending">⏳ Pending</option>
                <option value="completed">✅ Completed</option>
              </select>
            </div>

            {/* Priority Filter */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
                <svg className="w-4 h-4 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                Priority
                {filters.priority?.length ? (
                  <span className="ml-auto px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full font-bold">
                    {filters.priority.length}
                  </span>
                ) : null}
              </label>
              <select
                multiple
                value={filters.priority || []}
                onChange={(e) => {
                  const selected = Array.from(e.target.selectedOptions, option => option.value)
                  setFilters({ ...filters, priority: selected.length > 0 ? selected : undefined })
                }}
                className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg text-gray-900 focus:border-red-500 focus:ring-2 focus:ring-red-200 transition-all font-medium"
                size={4}
              >
                <option value="low">🟢 Low</option>
                <option value="medium">🟡 Medium</option>
                <option value="high">🟠 High</option>
                <option value="urgent">🔴 Urgent</option>
              </select>
              <p className="text-xs text-gray-600 mt-1 font-medium">💡 Hold Ctrl/Cmd to select multiple</p>
            </div>

            {/* Recurring Filter */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
                <svg className="w-4 h-4 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
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
                className="w-full px-3 py-3 border-2 border-gray-300 rounded-lg text-gray-900 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all font-medium"
              >
                <option value="all">📋 All Tasks</option>
                <option value="recurring">🔁 Recurring Only</option>
                <option value="one-time">📌 One-time Only</option>
              </select>
            </div>
          </div>

          {/* Date Range */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg">
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
                <svg className="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Due After
              </label>
              <input
                type="datetime-local"
                value={filters.dueAfter || ''}
                onChange={(e) => setFilters({ ...filters, dueAfter: e.target.value || undefined })}
                className="w-full px-3 py-3 border-2 border-gray-300 rounded-lg text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
                <svg className="w-4 h-4 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Due Before
              </label>
              <input
                type="datetime-local"
                value={filters.dueBefore || ''}
                onChange={(e) => setFilters({ ...filters, dueBefore: e.target.value || undefined })}
                className="w-full px-3 py-3 border-2 border-gray-300 rounded-lg text-gray-900 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
              />
            </div>
          </div>

          {/* Tags Input */}
          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
              <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
              Tags
              {filters.tags?.length ? (
                <span className="ml-auto px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full font-bold">
                  {filters.tags.length}
                </span>
              ) : null}
            </label>
            <div className="relative">
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
                className="w-full pl-10 pr-3 py-3 border-2 border-gray-300 rounded-lg text-gray-900 focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all"
              />
              <svg className="absolute left-3 top-3.5 w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
            </div>
            <p className="text-xs text-gray-600 mt-1 font-medium">💡 Separate multiple tags with commas</p>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t-2 border-gray-200">
            <button
              onClick={handleSearch}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 font-bold shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Apply Filters
              {activeFilterCount > 0 && (
                <span className="ml-1 px-2 py-0.5 bg-white text-blue-600 text-xs rounded-full font-bold">
                  {activeFilterCount}
                </span>
              )}
            </button>
            <button
              onClick={handleReset}
              className="flex items-center justify-center gap-2 px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-bold shadow-md hover:shadow-lg border-2 border-gray-300 transition-all duration-200"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
              Clear All
            </button>
          </div>

          {/* Active Filters Summary */}
          {activeFilterCount > 0 && (
            <div className="pt-4 border-t-2 border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-3">
                <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                </svg>
                <p className="text-sm font-bold text-gray-800">
                  Active Filters ({activeFilterCount}):
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                {filters.search && (
                  <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800 text-xs font-semibold rounded-full border border-blue-300">
                    🔍 "{filters.search}"
                  </span>
                )}
                {filters.status !== 'all' && (
                  <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-green-100 to-green-200 text-green-800 text-xs font-semibold rounded-full border border-green-300">
                    {filters.status === 'pending' ? '⏳ Pending' : '✅ Completed'}
                  </span>
                )}
                {filters.priority?.map(p => (
                  <span key={p} className="inline-flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-red-100 to-red-200 text-red-800 text-xs font-semibold rounded-full border border-red-300">
                    {p === 'low' ? '🟢' : p === 'medium' ? '🟡' : p === 'high' ? '🟠' : '🔴'} {p.charAt(0).toUpperCase() + p.slice(1)}
                  </span>
                ))}
                {filters.tags?.map(t => (
                  <span key={t} className="inline-flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-green-100 to-green-200 text-green-800 text-xs font-semibold rounded-full border border-green-300">
                    🏷️ {t}
                  </span>
                ))}
                {filters.isRecurring !== undefined && (
                  <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-purple-100 to-purple-200 text-purple-800 text-xs font-semibold rounded-full border border-purple-300">
                    {filters.isRecurring ? '🔁 Recurring' : '📌 One-time'}
                  </span>
                )}
                {filters.dueAfter && (
                  <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-orange-100 to-orange-200 text-orange-800 text-xs font-semibold rounded-full border border-orange-300">
                    📅 After: {new Date(filters.dueAfter).toLocaleDateString()}
                  </span>
                )}
                {filters.dueBefore && (
                  <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-orange-100 to-orange-200 text-orange-800 text-xs font-semibold rounded-full border border-orange-300">
                    📅 Before: {new Date(filters.dueBefore).toLocaleDateString()}
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

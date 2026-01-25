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
    <>
      <style jsx>{`
        .premium-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .premium-scrollbar::-webkit-scrollbar-track {
          background: linear-gradient(to bottom, #f3f4f6, #e5e7eb);
          border-radius: 10px;
        }
        .premium-scrollbar::-webkit-scrollbar-thumb {
          background: linear-gradient(to bottom, #3b82f6, #8b5cf6);
          border-radius: 10px;
          transition: all 0.3s ease;
        }
        .premium-scrollbar::-webkit-scrollbar-thumb:hover {
          background: linear-gradient(to bottom, #2563eb, #7c3aed);
        }
        .glass-panel {
          background: rgba(255, 255, 255, 0.9);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
        }
        .slim-input {
          height: 38px;
        }
        .slim-select {
          height: 38px;
        }
      `}</style>
      
      <div className="glass-panel p-6 rounded-2xl shadow-[0_8px_32px_rgba(31,38,135,0.15)] mb-6 border border-white/40">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2.5 rounded-xl shadow-lg">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent tracking-tight">
                Advanced Search & Filters
              </h3>
              {activeFilterCount > 0 && (
                <p className="text-xs text-gray-500 font-medium mt-0.5">
                  {activeFilterCount} filter{activeFilterCount > 1 ? 's' : ''} active
                </p>
              )}
            </div>
          </div>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 font-medium text-sm transition-all duration-300 shadow-md hover:shadow-lg hover:scale-[1.02]"
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
          <div className="mt-6 space-y-4 glass-panel p-6 rounded-xl shadow-inner border border-gray-100/50">
            {/* Search Input */}
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-2 flex items-center gap-1.5 tracking-wide uppercase">
                <svg className="w-3.5 h-3.5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                Search (Title/Description)
              </label>
              <div className="relative group">
                <input
                  type="text"
                  placeholder="Search tasks by title or description..."
                  value={filters.search || ''}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value || undefined })}
                  className="slim-input w-full pl-9 pr-3 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-700 bg-white/80 focus:bg-white focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all duration-300 hover:border-gray-300 placeholder:text-gray-400"
                />
                <svg className="absolute left-3 top-2.5 w-4 h-4 text-gray-400 group-focus-within:text-blue-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {/* Status Filter */}
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-2 flex items-center gap-1.5 tracking-wide uppercase">
                  <svg className="w-3.5 h-3.5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Status
                </label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value as any })}
                  className="slim-select w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-700 bg-white/80 focus:bg-white focus:border-green-400 focus:ring-2 focus:ring-green-100 transition-all duration-300 hover:border-gray-300 font-medium cursor-pointer"
                >
                  <option value="all">📋 All Tasks</option>
                  <option value="pending">⏳ Pending</option>
                  <option value="completed">✅ Completed</option>
                </select>
              </div>

              {/* Priority Filter */}
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-2 flex items-center gap-1.5 tracking-wide uppercase">
                  <svg className="w-3.5 h-3.5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  Priority
                  {filters.priority?.length ? (
                    <span className="ml-auto px-1.5 py-0.5 bg-gradient-to-r from-red-500 to-pink-500 text-white text-[10px] rounded-full font-bold shadow-sm">
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
                  className="premium-scrollbar w-full px-3 py-2 border border-gray-200 rounded-xl text-sm text-gray-700 bg-white/80 focus:bg-white focus:border-red-400 focus:ring-2 focus:ring-red-100 transition-all duration-300 hover:border-gray-300 font-medium cursor-pointer"
                  size={4}
                >
                  <option value="low">🟢 Low</option>
                  <option value="medium">🟡 Medium</option>
                  <option value="high">🟠 High</option>
                  <option value="urgent">🔴 Urgent</option>
                </select>
                <p className="text-[10px] text-gray-500 mt-1.5 font-medium">💡 Hold Ctrl/Cmd to select multiple</p>
              </div>

              {/* Recurring Filter */}
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-2 flex items-center gap-1.5 tracking-wide uppercase">
                  <svg className="w-3.5 h-3.5 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
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
                  className="slim-select w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-700 bg-white/80 focus:bg-white focus:border-purple-400 focus:ring-2 focus:ring-purple-100 transition-all duration-300 hover:border-gray-300 font-medium cursor-pointer"
                >
                  <option value="all">📋 All Tasks</option>
                  <option value="recurring">🔁 Recurring Only</option>
                  <option value="one-time">📌 One-time Only</option>
                </select>
              </div>
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 glass-panel p-4 rounded-xl border border-gray-100/50">
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-2 flex items-center gap-1.5 tracking-wide uppercase">
                  <svg className="w-3.5 h-3.5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  Due After
                </label>
                <input
                  type="datetime-local"
                  value={filters.dueAfter || ''}
                  onChange={(e) => setFilters({ ...filters, dueAfter: e.target.value || undefined })}
                  className="slim-input w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-700 bg-white/80 focus:bg-white focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all duration-300 hover:border-gray-300 cursor-pointer"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-2 flex items-center gap-1.5 tracking-wide uppercase">
                  <svg className="w-3.5 h-3.5 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  Due Before
                </label>
                <input
                  type="datetime-local"
                  value={filters.dueBefore || ''}
                  onChange={(e) => setFilters({ ...filters, dueBefore: e.target.value || undefined })}
                  className="slim-input w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-700 bg-white/80 focus:bg-white focus:border-purple-400 focus:ring-2 focus:ring-purple-100 transition-all duration-300 hover:border-gray-300 cursor-pointer"
                />
              </div>
            </div>

            {/* Tags Input */}
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-2 flex items-center gap-1.5 tracking-wide uppercase">
                <svg className="w-3.5 h-3.5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
                Tags
                {filters.tags?.length ? (
                  <span className="ml-auto px-1.5 py-0.5 bg-gradient-to-r from-green-500 to-emerald-500 text-white text-[10px] rounded-full font-bold shadow-sm">
                    {filters.tags.length}
                  </span>
                ) : null}
              </label>
              <div className="relative group">
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
                  className="slim-input w-full pl-9 pr-3 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-700 bg-white/80 focus:bg-white focus:border-green-400 focus:ring-2 focus:ring-green-100 transition-all duration-300 hover:border-gray-300 placeholder:text-gray-400"
                />
                <svg className="absolute left-3 top-2.5 w-4 h-4 text-gray-400 group-focus-within:text-green-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
              </div>
              <p className="text-[10px] text-gray-500 mt-1.5 font-medium">💡 Separate multiple tags with commas</p>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-2.5 pt-4 border-t border-gray-200/50">
              <button
                onClick={handleSearch}
                className="flex-1 flex items-center justify-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 font-semibold text-sm shadow-lg hover:shadow-xl transform hover:scale-[1.02] transition-all duration-300"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                Apply Filters
                {activeFilterCount > 0 && (
                  <span className="ml-1 px-1.5 py-0.5 bg-white text-blue-600 text-[10px] rounded-full font-bold shadow-sm">
                    {activeFilterCount}
                  </span>
                )}
              </button>
              <button
                onClick={handleReset}
                className="flex items-center justify-center gap-2 px-5 py-2.5 glass-panel text-gray-600 rounded-xl hover:bg-gray-50 font-semibold text-sm shadow-md hover:shadow-lg border border-gray-200 transition-all duration-300 hover:scale-[1.02]"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Clear All
              </button>
            </div>

            {/* Active Filters Summary */}
            {activeFilterCount > 0 && (
              <div className="pt-4 border-t border-gray-200/50 glass-panel p-4 rounded-xl">
                <div className="flex items-center gap-2 mb-3">
                  <svg className="w-4 h-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                  </svg>
                  <p className="text-xs font-bold text-gray-700 tracking-wide uppercase">
                    Active Filters ({activeFilterCount}):
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {filters.search && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-[11px] font-semibold rounded-lg shadow-sm">
                      🔍 "{filters.search}"
                    </span>
                  )}
                  {filters.status !== 'all' && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-gradient-to-r from-green-500 to-emerald-600 text-white text-[11px] font-semibold rounded-lg shadow-sm">
                      {filters.status === 'pending' ? '⏳ Pending' : '✅ Completed'}
                    </span>
                  )}
                  {filters.priority?.map(p => (
                    <span key={p} className="inline-flex items-center gap-1 px-2.5 py-1 bg-gradient-to-r from-red-500 to-pink-600 text-white text-[11px] font-semibold rounded-lg shadow-sm">
                      {p === 'low' ? '🟢' : p === 'medium' ? '🟡' : p === 'high' ? '🟠' : '🔴'} {p.charAt(0).toUpperCase() + p.slice(1)}
                    </span>
                  ))}
                  {filters.tags?.map(t => (
                    <span key={t} className="inline-flex items-center gap-1 px-2.5 py-1 bg-gradient-to-r from-green-500 to-emerald-600 text-white text-[11px] font-semibold rounded-lg shadow-sm">
                      🏷️ {t}
                    </span>
                  ))}
                  {filters.isRecurring !== undefined && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-gradient-to-r from-purple-500 to-purple-600 text-white text-[11px] font-semibold rounded-lg shadow-sm">
                      {filters.isRecurring ? '🔁 Recurring' : '📌 One-time'}
                    </span>
                  )}
                  {filters.dueAfter && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-gradient-to-r from-orange-500 to-orange-600 text-white text-[11px] font-semibold rounded-lg shadow-sm">
                      📅 After: {new Date(filters.dueAfter).toLocaleDateString()}
                    </span>
                  )}
                  {filters.dueBefore && (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-gradient-to-r from-orange-500 to-orange-600 text-white text-[11px] font-semibold rounded-lg shadow-sm">
                      📅 Before: {new Date(filters.dueBefore).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  )
}

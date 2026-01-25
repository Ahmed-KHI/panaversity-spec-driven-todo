'use client'

import { useRouter } from 'next/navigation'
import { AuthUser } from '@/lib/auth'
import { useState } from 'react'

interface HeaderProps {
  user: AuthUser
}

export default function Header({ user }: HeaderProps) {
  const router = useRouter()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST' })
    window.location.href = '/login'
  }

  return (
    <header className="glass sticky top-0 z-50 border-b border-white/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 sm:py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3 sm:gap-6">
            <h1 className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              ✨ Todo
            </h1>
            
            {/* Desktop Navigation */}
            <nav className="hidden md:flex gap-3">
              <button
                onClick={() => router.push('/dashboard')}
                className="group px-4 lg:px-5 py-2 lg:py-2.5 text-sm font-medium text-gray-700 hover:text-indigo-600 bg-white/50 hover:bg-white/80 rounded-xl transition-all hover:scale-105 hover:shadow-lg backdrop-blur-sm border border-white/30"
              >
                <span className="flex items-center gap-2">
                  📊 <span className="hidden lg:inline group-hover:tracking-wide transition-all">Dashboard</span>
                </span>
              </button>
              <button
                onClick={() => router.push('/chat')}
                className="group px-4 lg:px-5 py-2 lg:py-2.5 text-sm font-medium text-gray-700 hover:text-indigo-600 bg-white/50 hover:bg-white/80 rounded-xl transition-all hover:scale-105 hover:shadow-lg backdrop-blur-sm border border-white/30"
              >
                <span className="flex items-center gap-2">
                  💬 <span className="hidden lg:inline group-hover:tracking-wide transition-all">AI Chat</span>
                </span>
              </button>
            </nav>
          </div>
          
          <div className="flex items-center gap-2 sm:gap-4">
            {/* User Email - Hidden on small screens */}
            <div className="hidden sm:block px-3 sm:px-4 py-2 bg-white/60 rounded-xl border border-white/40 backdrop-blur-sm">
              <span className="text-xs sm:text-sm font-medium bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent truncate max-w-[120px] sm:max-w-none">{user.email}</span>
            </div>
            
            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="px-3 sm:px-5 py-2 sm:py-2.5 text-xs sm:text-sm font-medium text-white bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 shadow-lg hover:shadow-xl hover:scale-105 transition-all"
            >
              🚪 <span className="hidden sm:inline">Logout</span>
            </button>
            
            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-gray-700 hover:text-indigo-600 bg-white/50 hover:bg-white/80 rounded-xl transition-all border border-white/30"
              aria-label="Toggle menu"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {mobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
        
        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-4 pb-4 space-y-2 border-t border-white/20 pt-4">
            <button
              onClick={() => { router.push('/dashboard'); setMobileMenuOpen(false); }}
              className="w-full flex items-center gap-3 px-4 py-3 text-sm font-medium text-gray-700 hover:text-indigo-600 bg-white/50 hover:bg-white/80 rounded-xl transition-all border border-white/30"
            >
              📊 Dashboard
            </button>
            <button
              onClick={() => { router.push('/chat'); setMobileMenuOpen(false); }}
              className="w-full flex items-center gap-3 px-4 py-3 text-sm font-medium text-gray-700 hover:text-indigo-600 bg-white/50 hover:bg-white/80 rounded-xl transition-all border border-white/30"
            >
              💬 AI Chat
            </button>
            <div className="sm:hidden px-4 py-3 bg-white/60 rounded-xl border border-white/40">
              <span className="text-xs font-medium text-gray-600">{user.email}</span>
            </div>
          </div>
        )}
      </div>
    </header>
  )
}

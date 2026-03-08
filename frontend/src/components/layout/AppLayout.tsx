import React from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const navItems = [
  { path: '/focus', label: 'Focus', icon: '🎯' },
  { path: '/analytics', label: 'Analytics', icon: '📊' },
  { path: '/settings/integrations', label: 'Integrations', icon: '🔗' },
]

export function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-deep-slate flex flex-col">
      <header className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <Link to="/focus" className="text-soft-mint font-bold text-xl tracking-tight">
          Sift
        </Link>
        <nav className="hidden md:flex items-center gap-6">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`text-sm transition-colors ${
                location.pathname === item.path
                  ? 'text-soft-mint'
                  : 'text-muted-text hover:text-off-white'
              }`}
            >
              {item.icon} {item.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-3">
          <span className="text-muted-text text-sm hidden md:block">
            {user?.full_name || user?.email}
          </span>
          <button
            onClick={handleLogout}
            className="text-muted-text text-sm hover:text-off-white transition-colors"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="flex-1 flex flex-col">
        {children}
      </main>

      <nav className="md:hidden border-t border-slate-800 flex">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex-1 flex flex-col items-center py-3 text-xs transition-colors ${
              location.pathname === item.path
                ? 'text-soft-mint'
                : 'text-muted-text'
            }`}
          >
            <span className="text-lg">{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </nav>
    </div>
  )
}

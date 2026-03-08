import { Navigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoading, token } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-deep-slate flex items-center justify-center">
        <div className="text-soft-mint text-lg animate-pulse">Loading...</div>
      </div>
    )
  }

  if (!token) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

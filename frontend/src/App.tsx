import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ProtectedRoute } from './components/layout/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import FocusPage from './pages/FocusPage'
import FreshStartPage from './pages/FreshStartPage'
import AnalyticsPage from './pages/AnalyticsPage'
import IntegrationsPage from './pages/Settings/IntegrationsPage'
import AdminDashboard from './pages/Admin/AdminDashboard'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Fresh start (protected but no layout) */}
          <Route path="/fresh-start" element={
            <ProtectedRoute><FreshStartPage /></ProtectedRoute>
          } />

          {/* Protected app routes */}
          <Route path="/check-in" element={<Navigate to="/focus" replace />} />
          <Route path="/focus" element={
            <ProtectedRoute><FocusPage /></ProtectedRoute>
          } />
          <Route path="/analytics" element={
            <ProtectedRoute><AnalyticsPage /></ProtectedRoute>
          } />
          <Route path="/settings/integrations" element={
            <ProtectedRoute><IntegrationsPage /></ProtectedRoute>
          } />
          <Route path="/admin" element={
            <ProtectedRoute><AdminDashboard /></ProtectedRoute>
          } />

          {/* Auth callback */}
          <Route path="/auth/callback" element={<AuthCallbackPage />} />

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/focus" replace />} />
          <Route path="*" element={<Navigate to="/focus" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

function AuthCallbackPage() {
  const params = new URLSearchParams(window.location.search)
  const accessToken = params.get('access_token')
  const refreshToken = params.get('refresh_token')

  if (accessToken && refreshToken) {
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refreshToken)
    window.location.href = '/focus'
  } else {
    window.location.href = '/login'
  }

  return (
    <div className="min-h-screen bg-deep-slate flex items-center justify-center">
      <div className="text-soft-mint animate-pulse">Authenticating...</div>
    </div>
  )
}

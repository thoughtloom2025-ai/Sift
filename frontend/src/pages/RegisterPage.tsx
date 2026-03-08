import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '../context/AuthContext'

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)
    try {
      await register(email, password, fullName)
      navigate('/focus')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'Registration failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-deep-slate flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-soft-mint mb-2">Sift</h1>
          <p className="text-muted-text">One task at a time.</p>
        </div>

        <div className="bg-slate-900 rounded-2xl p-8 border border-slate-800">
          <h2 className="text-off-white text-xl font-semibold mb-6">Create Account</h2>

          {error && (
            <div className="bg-amber-500/10 border border-amber-500/20 text-muted-amber rounded-lg p-3 mb-4 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-muted-text text-sm mb-1.5">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-off-white placeholder-muted-text focus:outline-none focus:border-soft-mint transition-colors"
                placeholder="Jane Smith"
                required
              />
            </div>
            <div>
              <label className="block text-muted-text text-sm mb-1.5">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-off-white placeholder-muted-text focus:outline-none focus:border-soft-mint transition-colors"
                placeholder="you@example.com"
                required
              />
            </div>
            <div>
              <label className="block text-muted-text text-sm mb-1.5">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-off-white placeholder-muted-text focus:outline-none focus:border-soft-mint transition-colors"
                placeholder="••••••••"
                required
                minLength={8}
              />
            </div>
            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              type="submit"
              disabled={isLoading}
              className="w-full bg-soft-mint text-deep-slate font-semibold py-3 rounded-lg hover:bg-emerald-400 transition-colors disabled:opacity-50"
            >
              {isLoading ? 'Creating account...' : 'Create Account'}
            </motion.button>
          </form>

          <p className="text-muted-text text-sm text-center mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-soft-mint hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}

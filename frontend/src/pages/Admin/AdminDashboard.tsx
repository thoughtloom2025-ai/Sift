import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { AppLayout } from '../../components/layout/AppLayout'
import { api } from '../../services/api'

interface AdminStats {
  total_users: number
  active_users: number
  total_tasks: number
  tasks_completed_today: number
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/admin/stats')
        setStats(response.data)
      } catch {
        // ignore
      } finally {
        setIsLoading(false)
      }
    }
    fetchStats()
  }, [])

  return (
    <AppLayout>
      <div className="flex-1 px-4 py-12 max-w-4xl mx-auto w-full">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-2xl font-bold text-off-white mb-2">Admin Dashboard</h1>
          <p className="text-muted-text mb-8">System-wide statistics.</p>

          {isLoading ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="bg-slate-900 rounded-2xl p-6 animate-pulse h-24" />
              ))}
            </div>
          ) : stats ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Total Users', value: stats.total_users, color: 'text-soft-mint' },
                { label: 'Active Users', value: stats.active_users, color: 'text-soft-mint' },
                { label: 'Total Tasks', value: stats.total_tasks, color: 'text-off-white' },
                { label: 'Completed Today', value: stats.tasks_completed_today, color: 'text-muted-amber' },
              ].map((stat, i) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="bg-slate-900 rounded-2xl p-6 border border-slate-800"
                >
                  <p className="text-muted-text text-sm mb-1">{stat.label}</p>
                  <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
                </motion.div>
              ))}
            </div>
          ) : (
            <p className="text-muted-text">Failed to load stats. Admin access required.</p>
          )}
        </motion.div>
      </div>
    </AppLayout>
  )
}

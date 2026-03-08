import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { AppLayout } from '../components/layout/AppLayout'
import { api } from '../services/api'
import type { AnalyticsSummary } from '../types'

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await api.get('/analytics/summary')
        setSummary(response.data)
      } catch {
        // ignore
      } finally {
        setIsLoading(false)
      }
    }
    fetchSummary()
  }, [])

  const stats = summary ? [
    { label: 'Completed (7d)', value: summary.total_completed, color: 'text-soft-mint' },
    { label: 'Big Rocks Done', value: summary.big_rocks_completed, color: 'text-muted-amber' },
    { label: 'Active Tasks', value: summary.tasks_active, color: 'text-off-white' },
    { label: 'Avg Energy', value: `${summary.avg_energy}/5`, color: 'text-soft-mint' },
    { label: 'Fresh Starts', value: summary.fresh_start_count, color: 'text-muted-text' },
  ] : []

  return (
    <AppLayout>
      <div className="flex-1 px-4 py-12 max-w-2xl mx-auto w-full">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-2xl font-bold text-off-white mb-2">Analytics</h1>
          <p className="text-muted-text mb-8">Your focus patterns over time.</p>

          {isLoading ? (
            <div className="grid grid-cols-2 gap-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="bg-slate-900 rounded-2xl p-6 animate-pulse h-24" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4">
              {stats.map((stat, i) => (
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
          )}
        </motion.div>
      </div>
    </AppLayout>
  )
}

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useFreshStart } from '../hooks/useFreshStart'
import type { FreshStartReset } from '../types'

export default function FreshStartPage() {
  const { freshStartData, isLoading, triggerReset } = useFreshStart()
  const navigate = useNavigate()
  const [resetResult, setResetResult] = useState<FreshStartReset | null>(null)
  const [isResetting, setIsResetting] = useState(false)

  useEffect(() => {
    if (!isLoading && freshStartData && !freshStartData.should_trigger) {
      navigate('/focus', { replace: true })
    }
  }, [freshStartData, isLoading, navigate])

  const handleReset = async () => {
    setIsResetting(true)
    const result = await triggerReset()
    setResetResult(result)
    setIsResetting(false)
  }

  const handleContinue = () => {
    navigate('/focus')
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-deep-slate flex items-center justify-center">
        <div className="text-soft-mint animate-pulse text-lg">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-deep-slate flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md text-center"
      >
        {!resetResult ? (
          <>
            <div className="text-6xl mb-6">🌅</div>
            <h1 className="text-3xl font-bold text-off-white mb-3">Welcome back</h1>
            <p className="text-muted-text mb-2">
              You've been away for {freshStartData ? Math.round(freshStartData.hours_since_last_login) : 0} hours.
            </p>
            <p className="text-muted-text mb-8">
              Let's clear the old and start fresh.
            </p>

            <div className="bg-slate-900 rounded-2xl p-6 border border-slate-800 mb-6 text-left">
              <p className="text-off-white font-medium mb-2">Fresh Start will:</p>
              <ul className="text-muted-text text-sm space-y-2">
                <li>• Archive old tasks from before your break</li>
                <li>• Surface your single best next action</li>
                <li>• Let you start fresh without the pile</li>
              </ul>
            </div>

            <div className="flex flex-col gap-3">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleReset}
                disabled={isResetting}
                className="w-full py-4 bg-soft-mint text-deep-slate font-semibold rounded-xl text-lg hover:bg-emerald-400 transition-colors disabled:opacity-50"
              >
                {isResetting ? 'Clearing...' : 'Fresh Start →'}
              </motion.button>
              <button
                onClick={handleContinue}
                className="text-muted-text text-sm hover:text-off-white transition-colors"
              >
                Skip, keep my tasks
              </button>
            </div>
          </>
        ) : (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="text-6xl mb-6">✨</div>
            <h1 className="text-3xl font-bold text-off-white mb-3">All clear</h1>
            <p className="text-muted-text mb-6">{resetResult.message}</p>

            {resetResult.tasks_archived > 0 && (
              <div className="bg-slate-900 rounded-2xl p-4 border border-slate-800 mb-6">
                <p className="text-muted-text text-sm">
                  {resetResult.tasks_archived} tasks archived
                </p>
              </div>
            )}

            {resetResult.next_action_task && (
              <div className="bg-slate-900 rounded-2xl p-5 border border-soft-mint/20 mb-6 text-left">
                <p className="text-soft-mint text-xs font-semibold mb-2">SUGGESTED NEXT ACTION</p>
                <p className="text-off-white font-medium">{resetResult.next_action_task.title}</p>
              </div>
            )}

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleContinue}
              className="w-full py-4 bg-soft-mint text-deep-slate font-semibold rounded-xl text-lg hover:bg-emerald-400 transition-colors"
            >
              Let's Go →
            </motion.button>
          </motion.div>
        )}
      </motion.div>
    </div>
  )
}

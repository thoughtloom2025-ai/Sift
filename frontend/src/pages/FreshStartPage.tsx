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

  if (isLoading) {
    return (
      <div className="min-h-screen bg-deep-slate flex items-center justify-center">
        <motion.div
          animate={{ opacity: [0.3, 1, 0.3] }}
          transition={{ duration: 1.8, repeat: Infinity }}
          className="text-soft-mint text-2xl"
        >
          ◎
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-deep-slate flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ type: 'spring', stiffness: 260, damping: 28 }}
        className="w-full max-w-md text-center"
      >
        {!resetResult ? (
          <>
            <h1 className="text-4xl font-bold text-off-white mb-4 leading-tight">
              You've been away.
            </h1>
            <p className="text-muted-text text-lg mb-10 leading-readable">
              Let's not carry yesterday's weight.
            </p>

            <div className="bg-[#1E2235] rounded-2xl p-6 border border-slate-700/60 mb-8 text-left">
              <p className="text-off-white font-medium mb-3">A Fresh Start will:</p>
              <ul className="text-muted-text text-sm space-y-2 leading-readable">
                <li>· Archive tasks from before your break</li>
                <li>· Surface your single best next action</li>
                <li>· Let you begin without the pile</li>
              </ul>
            </div>

            <div className="flex flex-col gap-3">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.97 }}
                onClick={handleReset}
                disabled={isResetting}
                className="w-full py-4 bg-soft-mint text-deep-slate font-semibold
                           rounded-xl text-lg hover:brightness-105 transition-all
                           disabled:opacity-50"
              >
                {isResetting ? 'Clearing…' : 'Clear & Begin →'}
              </motion.button>
              <button
                onClick={() => navigate('/focus')}
                className="text-muted-text text-sm hover:text-off-white transition-colors py-2"
              >
                Keep my tasks, continue
              </button>
            </div>
          </>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: 'spring', stiffness: 260, damping: 28 }}
          >
            <h1 className="text-4xl font-bold text-off-white mb-3">
              You're clear.
            </h1>
            <p className="text-muted-text mb-8 leading-readable">{resetResult.message}</p>

            {resetResult.tasks_archived > 0 && (
              <div className="inline-block bg-slate-700/40 rounded-full px-4 py-1.5 mb-6">
                <span className="text-muted-text text-sm">
                  {resetResult.tasks_archived} tasks cleared
                </span>
              </div>
            )}

            {resetResult.next_action_task && (
              <div className="bg-[#1E2235] rounded-2xl p-5 border border-soft-mint/20 mb-8 text-left">
                <p className="text-soft-mint text-xs font-semibold mb-2 tracking-wide uppercase">
                  Your first move
                </p>
                <p className="text-off-white font-medium leading-readable">
                  {resetResult.next_action_task.title}
                </p>
              </div>
            )}

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => navigate('/focus')}
              className="w-full py-4 bg-soft-mint text-deep-slate font-semibold
                         rounded-xl text-lg hover:brightness-105 transition-all"
            >
              Let's Go →
            </motion.button>
          </motion.div>
        )}
      </motion.div>
    </div>
  )
}

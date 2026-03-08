import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import type { Task } from '../../types'

interface TaskCardProps {
  task: Task
  onComplete: (taskId: number) => Promise<void>
  onSnooze: (taskId: number, duration: number) => Promise<void>
  onBreakdown: (taskId: number) => Promise<string[]>
}

const sourceLabels: Record<string, string> = {
  gmail: '📧 Gmail',
  slack: '💬 Slack',
  notion: '📝 Notion',
  manual: '✍️ Manual',
}

export function TaskCard({ task, onComplete, onSnooze, onBreakdown }: TaskCardProps) {
  const [isCompleting, setIsCompleting] = useState(false)
  const [isBreakingDown, setIsBreakingDown] = useState(false)
  const [subSteps, setSubSteps] = useState<string[]>(task.sub_steps || [])

  const handleComplete = async () => {
    setIsCompleting(true)
    await onComplete(task.id)
  }

  const handleBreakdown = async () => {
    setIsBreakingDown(true)
    const steps = await onBreakdown(task.id)
    setSubSteps(steps)
    setIsBreakingDown(false)
  }

  const energyDots = Array.from({ length: 5 }, (_, i) => i < task.energy_required)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className={`w-full max-w-lg rounded-2xl p-6 shadow-2xl ${
        task.is_big_rock
          ? 'bg-cloud-gray border-2 border-muted-amber/40'
          : 'bg-cloud-gray'
      }`}
    >
      {task.is_big_rock && (
        <div className="flex items-center gap-2 mb-3 text-muted-amber text-sm font-semibold">
          <span>🪨</span>
          <span>Big Rock</span>
        </div>
      )}

      <div className="flex items-start justify-between gap-3 mb-3">
        <h2 className="text-deep-slate font-semibold text-xl leading-tight">
          {task.title}
        </h2>
        <span className="text-xs text-slate-500 shrink-0 mt-1">
          {sourceLabels[task.source]}
        </span>
      </div>

      {task.description && (
        <p className="text-slate-600 text-sm mb-4 leading-relaxed">
          {task.description}
        </p>
      )}

      <div className="flex items-center gap-4 mb-4 text-sm text-slate-500">
        <span>Energy: {energyDots.map((filled, i) => (
          <span key={i} className={filled ? 'text-soft-mint' : 'text-slate-300'}>●</span>
        ))}</span>
        <span>Impact: {task.impact}/5</span>
        <span>Urgency: {task.urgency}/5</span>
      </div>

      <AnimatePresence>
        {subSteps.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-4 bg-slate-100 rounded-xl p-4"
          >
            <p className="text-slate-500 text-xs font-semibold mb-2">STEPS</p>
            <ol className="space-y-2">
              {subSteps.map((step, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                  <span className="text-soft-mint font-bold shrink-0">{i + 1}.</span>
                  {step}
                </li>
              ))}
            </ol>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex flex-col gap-3">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleComplete}
          disabled={isCompleting}
          className="w-full py-3 bg-soft-mint text-deep-slate font-semibold rounded-xl transition-colors hover:bg-emerald-400 disabled:opacity-50"
        >
          {isCompleting ? 'Completing...' : '✓ Done'}
        </motion.button>

        <div className="flex gap-2">
          {task.is_big_rock && subSteps.length === 0 && (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleBreakdown}
              disabled={isBreakingDown}
              className="flex-1 py-2.5 bg-muted-amber/20 text-muted-amber font-medium rounded-xl text-sm hover:bg-muted-amber/30 disabled:opacity-50 transition-colors"
            >
              {isBreakingDown ? 'Breaking down...' : '🔨 Break Down'}
            </motion.button>
          )}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onSnooze(task.id, 60)}
            className="flex-1 py-2.5 bg-slate-200/50 text-slate-600 font-medium rounded-xl text-sm hover:bg-slate-200/70 transition-colors"
          >
            💤 Snooze 1hr
          </motion.button>
        </div>
      </div>
    </motion.div>
  )
}

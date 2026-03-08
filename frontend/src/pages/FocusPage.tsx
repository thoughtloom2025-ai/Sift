import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { TaskCard } from '../components/TaskCard/TaskCard'
import { EnergyGate } from '../components/EnergyGate/EnergyGate'
import { AppLayout } from '../components/layout/AppLayout'
import { useTasks } from '../hooks/useTasks'
import { useEnergy } from '../hooks/useEnergy'

type AppState = 'ENERGY_GATE' | 'FOCUSED' | 'FOCUS_MODE'

export default function FocusPage() {
  const { setEnergyLevel, submitEnergy, isSubmitting } = useEnergy()
  const [confirmedEnergy, setConfirmedEnergy] = useState<number | null>(null)
  const [appState, setAppState] = useState<AppState>('ENERGY_GATE')
  const [noMoreTasks, setNoMoreTasks] = useState(false)

  const {
    task,
    isLoading,
    error,
    fetchNext,
    fetchEligible,
    completeTask,
    snoozeTask,
    breakdownTask,
  } = useTasks(confirmedEnergy ?? 3)

  useEffect(() => {
    if (confirmedEnergy !== null) {
      setNoMoreTasks(false)
      fetchNext()
      fetchEligible()
    }
  }, [confirmedEnergy]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (confirmedEnergy !== null && !isLoading && !task && !error) {
      setNoMoreTasks(true)
    }
  }, [isLoading, task, error, confirmedEnergy])

  // Transition to FOCUS_MODE 2s after a task first appears
  useEffect(() => {
    if (task && appState === 'FOCUSED') {
      const timer = setTimeout(() => setAppState('FOCUS_MODE'), 2000)
      return () => clearTimeout(timer)
    }
  }, [task, appState])

  const handleEnergyConfirm = async (value: number) => {
    setEnergyLevel(value)
    const success = await submitEnergy(value)
    if (success) {
      setConfirmedEnergy(value)
      setAppState('FOCUSED')
    }
  }

  const handleExitFocusMode = () => setAppState('FOCUSED')

  // ── FOCUS MODE: fullscreen breathing background, no nav ─────────────────────
  if (appState === 'FOCUS_MODE' && task) {
    return (
      <motion.div
        animate={{ backgroundColor: ['#1A1C2E', '#1E2235', '#1A1C2E'] }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
        className="min-h-screen flex flex-col items-center justify-center px-4 py-12"
        onClick={handleExitFocusMode}
      >
        <p className="text-muted-text text-xs mb-8 opacity-40 select-none">
          tap anywhere to exit focus mode
        </p>

        {/* Stop click propagation so card interactions don't exit focus mode */}
        <div
          className="w-full max-w-lg"
          onClick={(e) => e.stopPropagation()}
        >
          <AnimatePresence mode="wait">
            <TaskCard
              key={task.id}
              task={task}
              onComplete={completeTask}
              onSnooze={snoozeTask}
              onBreakdown={breakdownTask}
            />
          </AnimatePresence>
        </div>
      </motion.div>
    )
  }

  // ── ENERGY GATE ─────────────────────────────────────────────────────────────
  if (appState === 'ENERGY_GATE') {
    return (
      <AppLayout>
        <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
          <AnimatePresence mode="wait">
            <EnergyGate
              onConfirm={handleEnergyConfirm}
              isSubmitting={isSubmitting}
            />
          </AnimatePresence>
        </div>
      </AppLayout>
    )
  }

  // ── FOCUSED: task visible, nav visible ──────────────────────────────────────
  return (
    <AppLayout>
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        <div className="w-full max-w-lg">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <p className="text-muted-text text-sm">Your current focus</p>
              <h1 className="text-off-white text-2xl font-bold">Next Task</h1>
            </div>
            <button
              onClick={() => setAppState('ENERGY_GATE')}
              className="text-muted-text text-sm hover:text-off-white transition-colors"
            >
              ⚡ Change energy
            </button>
          </div>

          {/* Loading */}
          {isLoading && (
            <div className="text-center py-20">
              <motion.div
                animate={{ opacity: [0.4, 1, 0.4] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="text-soft-mint text-4xl mb-4"
              >
                ◎
              </motion.div>
              <p className="text-muted-text">Finding your next task…</p>
            </div>
          )}

          {/* Error */}
          {error && !isLoading && (
            <div className="text-center py-20">
              <p className="text-muted-amber mb-4">{error}</p>
              <button onClick={fetchNext} className="text-soft-mint hover:underline">
                Try again
              </button>
            </div>
          )}

          {/* All clear */}
          {noMoreTasks && !isLoading && !error && (
            <div className="text-center py-20">
              <div className="text-5xl mb-4">🌿</div>
              <h2 className="text-off-white text-xl font-semibold mb-2">All clear</h2>
              <p className="text-muted-text mb-6">
                No tasks match your current energy level.
              </p>
              <button
                onClick={() => setAppState('ENERGY_GATE')}
                className="bg-soft-mint text-deep-slate font-semibold px-6 py-3
                           rounded-xl hover:brightness-105 transition-all"
              >
                Adjust energy
              </button>
            </div>
          )}

          {/* Task card */}
          <AnimatePresence mode="wait">
            {task && !isLoading && (
              <TaskCard
                key={task.id}
                task={task}
                onComplete={completeTask}
                onSnooze={snoozeTask}
                onBreakdown={breakdownTask}
              />
            )}
          </AnimatePresence>
        </div>
      </div>
    </AppLayout>
  )
}

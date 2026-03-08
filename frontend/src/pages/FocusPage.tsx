import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { TaskCard } from '../components/TaskCard/TaskCard'
import { EnergyGate } from '../components/EnergyGate/EnergyGate'
import { AppLayout } from '../components/layout/AppLayout'
import { AddTaskModal } from '../components/AddTaskModal/AddTaskModal'
import { useTasks } from '../hooks/useTasks'
import { useEnergy } from '../hooks/useEnergy'

type AppState = 'ENERGY_GATE' | 'FOCUSED' | 'FOCUS_MODE'

const ENERGY_OPTIONS: Record<number, { icon: string; label: string }> = {
  2: { icon: '🌊', label: 'Low' },
  3: { icon: '⚡', label: 'Mid' },
  5: { icon: '🔥', label: 'High' },
}

export default function FocusPage() {
  const { setEnergyLevel, submitEnergy, isSubmitting } = useEnergy()
  const [confirmedEnergy, setConfirmedEnergy] = useState<number | null>(null)
  const [appState, setAppState] = useState<AppState>('ENERGY_GATE')
  const [noMoreTasks, setNoMoreTasks] = useState(false)
  const [showAddModal, setShowAddModal] = useState(false)
  const [toast, setToast] = useState<string | null>(null)

  const {
    task,
    isLoading,
    error,
    fetchNext,
    fetchEligible,
    completeTask,
    snoozeTask,
    breakdownTask,
    createTask,
  } = useTasks(confirmedEnergy ?? 3)

  const showToast = (msg: string) => {
    setToast(msg)
    setTimeout(() => setToast(null), 3000)
  }

  const handleAddTask = async (title: string, description?: string) => {
    await createTask(title, description)
    showToast('Task added')
    await fetchNext()
    await fetchEligible()
  }

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
    } else if (task) {
      setNoMoreTasks(false)
    }
  }, [isLoading, task, error]) // eslint-disable-line react-hooks/exhaustive-deps


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
            <motion.button
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.96 }}
              onClick={() => setAppState('ENERGY_GATE')}
              title="Change energy level"
              className="flex flex-col items-center gap-1 px-4 py-2 rounded-xl
                         bg-slate-800/60 border border-slate-700 hover:border-slate-500
                         transition-colors group"
            >
              <span className="text-2xl leading-none">
                {confirmedEnergy !== null ? (ENERGY_OPTIONS[confirmedEnergy]?.icon ?? '⚡') : '⚡'}
              </span>
              <span className="text-xs font-medium text-muted-text group-hover:text-off-white transition-colors">
                {confirmedEnergy !== null ? (ENERGY_OPTIONS[confirmedEnergy]?.label ?? 'Energy') : 'Energy'}
              </span>
            </motion.button>
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
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={() => setAppState('ENERGY_GATE')}
                  className="bg-soft-mint text-deep-slate font-semibold px-6 py-3
                             rounded-xl hover:brightness-105 transition-all"
                >
                  Adjust energy
                </button>
                <button
                  onClick={() => setShowAddModal(true)}
                  className="bg-soft-mint/20 text-soft-mint font-semibold px-6 py-3
                             rounded-xl hover:bg-soft-mint/30 transition-all"
                >
                  + Add a task
                </button>
              </div>
            </div>
          )}

          {/* Task card */}
          <AnimatePresence mode="wait">
            {task && !isLoading && (
              <div
                onClick={(e) => {
                  if ((e.target as HTMLElement).closest('button')) return
                  setAppState('FOCUS_MODE')
                }}
                className="cursor-pointer group"
              >
                <TaskCard
                  key={task.id}
                  task={task}
                  onComplete={completeTask}
                  onSnooze={snoozeTask}
                  onBreakdown={breakdownTask}
                />
                <p className="text-center text-muted-text text-xs mt-3 opacity-0 group-hover:opacity-60 transition-opacity">
                  tap card to enter focus mode
                </p>
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Floating Add Button */}
      <button
        onClick={() => setShowAddModal(true)}
        className="fixed bottom-8 right-6 w-14 h-14 rounded-full bg-soft-mint
                   text-deep-slate text-2xl font-bold shadow-lg
                   hover:brightness-105 active:scale-95 transition-all z-30
                   flex items-center justify-center"
        aria-label="Add task"
      >
        +
      </button>

      {/* Toast */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="fixed bottom-28 left-1/2 -translate-x-1/2 z-50
                       bg-soft-mint text-deep-slate text-sm font-semibold
                       px-5 py-2 rounded-full shadow-lg"
          >
            {toast}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Add Task Modal */}
      <AddTaskModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSubmit={handleAddTask}
      />
    </AppLayout>
  )
}

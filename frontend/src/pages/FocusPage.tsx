import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { TaskCard } from '../components/TaskCard/TaskCard'
import { AppLayout } from '../components/layout/AppLayout'
import { EnergySlider } from '../components/EnergySlider/EnergySlider'
import { useTasks } from '../hooks/useTasks'
import { useEnergy } from '../hooks/useEnergy'
import type { Task } from '../types'

const SOURCE_LABELS: Record<string, string> = {
  gmail: 'Gmail',
  slack: 'Slack',
  notion: 'Notion',
  manual: 'Manual',
}

function EligibleTaskRow({ task, onSelect }: { task: Task; onSelect: (t: Task) => void }) {
  return (
    <motion.button
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      onClick={() => onSelect(task)}
      className="w-full text-left flex items-center gap-3 px-4 py-3 rounded-xl bg-cloud-gray/10 border border-cloud-gray/20 hover:border-soft-mint/40 hover:bg-cloud-gray/20 transition-all"
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          {task.is_big_rock && (
            <span className="text-xs font-semibold text-muted-amber border border-muted-amber/40 rounded px-1.5 py-0.5 shrink-0">
              Big Rock
            </span>
          )}
          <span className="text-off-white text-sm font-medium truncate">{task.title}</span>
        </div>
        <div className="flex items-center gap-3 text-xs text-muted-text">
          <span>{SOURCE_LABELS[task.source] ?? task.source}</span>
          <span>Energy {task.energy_required}/5</span>
          <span>Impact {task.impact}/5</span>
        </div>
      </div>
      <span className="text-muted-text text-xs shrink-0">Focus →</span>
    </motion.button>
  )
}

export default function FocusPage() {
  const { energyLevel: pendingEnergy, setEnergyLevel, submitEnergy, isSubmitting } = useEnergy()
  const [confirmedEnergy, setConfirmedEnergy] = useState<number | null>(null)
  const [editingEnergy, setEditingEnergy] = useState(false)
  const [showMore, setShowMore] = useState(false)
  const {
    task,
    eligibleTasks,
    isLoading,
    error,
    fetchNext,
    fetchEligible,
    selectTask,
    completeTask,
    snoozeTask,
    breakdownTask,
  } = useTasks(confirmedEnergy ?? 3)
  const [noMoreTasks, setNoMoreTasks] = useState(false)

  useEffect(() => {
    if (confirmedEnergy !== null) {
      setNoMoreTasks(false)
      setShowMore(false)
      fetchNext()
      fetchEligible()
    }
  }, [confirmedEnergy]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (confirmedEnergy !== null && !isLoading && !task && !error) {
      setNoMoreTasks(true)
    }
  }, [isLoading, task, error, confirmedEnergy])

  const handleConfirmEnergy = async () => {
    const success = await submitEnergy(pendingEnergy)
    if (success) {
      setConfirmedEnergy(pendingEnergy)
      setEditingEnergy(false)
    }
  }

  const handleSelectFromList = (selected: Task) => {
    selectTask(selected)
    setShowMore(false)
  }

  // Tasks shown in the list (exclude the current focus task)
  const otherTasks = eligibleTasks.filter((t) => t.id !== task?.id)

  if (confirmedEnergy === null || editingEnergy) {
    return (
      <AppLayout>
        <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-md text-center"
          >
            {editingEnergy && (
              <button
                onClick={() => setEditingEnergy(false)}
                className="mb-6 text-muted-text text-sm hover:text-off-white transition-colors block mx-auto"
              >
                ← Back to focus
              </button>
            )}
            <h1 className="text-3xl font-bold text-off-white mb-2">How's your bandwidth?</h1>
            <p className="text-muted-text mb-10">
              Be honest. Sift will match tasks to your energy.
            </p>

            <EnergySlider
              value={pendingEnergy}
              onChange={setEnergyLevel}
              disabled={isSubmitting}
            />

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleConfirmEnergy}
              disabled={isSubmitting || pendingEnergy === 0}
              className="mt-10 w-full py-4 bg-soft-mint text-deep-slate font-semibold rounded-xl text-lg hover:bg-emerald-400 transition-colors disabled:opacity-50"
            >
              {isSubmitting ? 'Loading...' : "Let's Focus →"}
            </motion.button>
          </motion.div>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        <div className="w-full max-w-lg">
          <div className="flex items-center justify-between mb-8">
            <div>
              <p className="text-muted-text text-sm">Your current focus</p>
              <h1 className="text-off-white text-2xl font-bold">Next Task</h1>
            </div>
            <button
              onClick={() => setEditingEnergy(true)}
              className="text-muted-text text-sm hover:text-off-white transition-colors flex items-center gap-1"
            >
              ⚡ Energy: {confirmedEnergy}/5
            </button>
          </div>

          {isLoading && (
            <div className="text-center py-20">
              <div className="text-soft-mint text-4xl mb-4 animate-pulse">⏳</div>
              <p className="text-muted-text">Finding your next task...</p>
            </div>
          )}

          {error && (
            <div className="text-center py-20">
              <p className="text-muted-amber mb-4">{error}</p>
              <button onClick={fetchNext} className="text-soft-mint hover:underline">
                Try again
              </button>
            </div>
          )}

          {noMoreTasks && !isLoading && !error && (
            <div className="text-center py-20">
              <div className="text-5xl mb-4">🎉</div>
              <h2 className="text-off-white text-xl font-semibold mb-2">All clear!</h2>
              <p className="text-muted-text mb-6">No tasks match your current energy level.</p>
              <button
                onClick={() => setEditingEnergy(true)}
                className="bg-soft-mint text-deep-slate font-semibold px-6 py-3 rounded-xl hover:bg-emerald-400 transition-colors"
              >
                Adjust Energy Level
              </button>
            </div>
          )}

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

          {/* Show More escape hatch — only when a task is shown and there are others */}
          {task && !isLoading && otherTasks.length > 0 && (
            <div className="mt-6">
              <button
                onClick={() => setShowMore((v) => !v)}
                className="w-full text-center text-muted-text text-sm hover:text-off-white transition-colors flex items-center justify-center gap-2 py-2"
              >
                <motion.span
                  animate={{ rotate: showMore ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                  className="inline-block"
                >
                  ▾
                </motion.span>
                {showMore
                  ? 'Hide task list'
                  : `Show ${otherTasks.length} more eligible task${otherTasks.length !== 1 ? 's' : ''}`}
              </button>

              <AnimatePresence>
                {showMore && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.25 }}
                    className="overflow-hidden mt-3 space-y-2"
                  >
                    {otherTasks.map((t) => (
                      <EligibleTaskRow key={t.id} task={t} onSelect={handleSelectFromList} />
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  )
}

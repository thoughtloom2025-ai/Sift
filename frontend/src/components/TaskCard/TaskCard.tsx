import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence, useMotionValue, useTransform } from 'framer-motion'
import type { Task } from '../../types'

interface TaskCardProps {
  task: Task
  onComplete: (taskId: number) => Promise<void>
  onSnooze: (taskId: number, duration: number) => Promise<void>
  onBreakdown: (taskId: number) => Promise<string[]>
}

// SVG ring: r=36 → circumference ≈ 226.2
const RADIUS = 36
const CIRC = 2 * Math.PI * RADIUS
const SNOOZE_MS = 60 * 60 * 1000 // 60 minutes

const SOURCE_LABELS: Record<string, string> = {
  gmail:  'Gmail',
  slack:  'Slack',
  notion: 'Notion',
  manual: 'Manual',
}

function energyBadge(level: number): { icon: string; label: string } {
  if (level <= 2) return { icon: '🌊', label: 'Low' }
  if (level <= 3) return { icon: '⚡', label: 'Mid' }
  return { icon: '🔥', label: 'High' }
}

function ProgressRing({ startTime }: { startTime: number }) {
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    // Update every 10s — no ticking digits, just gentle visual drift
    const id = setInterval(() => {
      setElapsed(Date.now() - startTime)
    }, 10_000)
    return () => clearInterval(id)
  }, [startTime])

  const progress = Math.min(elapsed / SNOOZE_MS, 1)
  const dashOffset = CIRC * (1 - progress)

  return (
    <div className="relative flex items-center justify-center" style={{ width: 80, height: 80 }}>
      <svg width="80" height="80" className="-rotate-90">
        {/* Track */}
        <circle
          cx="40" cy="40" r={RADIUS}
          fill="none"
          stroke="rgba(255,255,255,0.08)"
          strokeWidth="4"
        />
        {/* Soft Mint fill — grows as time passes toward auto-snooze */}
        <motion.circle
          cx="40" cy="40" r={RADIUS}
          fill="none"
          stroke="#B2D8C8"
          strokeWidth="4"
          strokeLinecap="round"
          strokeDasharray={CIRC}
          animate={{ strokeDashoffset: dashOffset }}
          transition={{ duration: 0.8, ease: 'easeInOut' }}
        />
      </svg>
      {/* Pulsing center dot */}
      <motion.div
        className="absolute w-2 h-2 rounded-full bg-soft-mint"
        animate={{ opacity: [0.4, 1, 0.4] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
      />
    </div>
  )
}

function BreakdownSkeleton() {
  return (
    <div className="space-y-3">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: [0.3, 0.7, 0.3] }}
          transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
          className="h-4 rounded-full bg-muted-amber/30"
          style={{ width: `${75 - i * 10}%` }}
        />
      ))}
    </div>
  )
}

export function TaskCard({ task, onComplete, onSnooze, onBreakdown }: TaskCardProps) {
  const [isCompleting, setIsCompleting]     = useState(false)
  const [isBreakingDown, setIsBreakingDown] = useState(false)
  const [subSteps, setSubSteps]             = useState<string[]>(task.sub_steps ?? [])
  const startTimeRef                         = useRef(Date.now())

  // Auto-snooze when the 60-min ring completes
  useEffect(() => {
    const timer = setTimeout(() => {
      onSnooze(task.id, 60)
    }, SNOOZE_MS)
    return () => clearTimeout(timer)
  }, [task.id, onSnooze])

  // Sync sub-steps and reset ring timer on new task
  useEffect(() => {
    setSubSteps(task.sub_steps ?? [])
    startTimeRef.current = Date.now()
  }, [task.id, task.sub_steps])

  const handleComplete = async () => {
    setIsCompleting(true)
    await onComplete(task.id)
  }

  const handleBreakdown = async () => {
    setIsBreakingDown(true)
    try {
      const steps = await onBreakdown(task.id)
      setSubSteps(steps)
    } finally {
      setIsBreakingDown(false)
    }
  }

  // Inverted hierarchy: micro-step gets top billing
  const microStep = subSteps.length > 0 ? subSteps[0] : `Begin: ${task.title}`

  // Swipe gesture motion values
  const x = useMotionValue(0)
  const snoozeOpacity = useTransform(x, [0, 80],   [0, 1])
  const doneOpacity   = useTransform(x, [-80, 0],  [1, 0])
  const cardOpacity   = useTransform(x, [-120, -80, 0, 80, 120], [0.6, 1, 1, 1, 0.6])

  const handleDragEnd = (_: unknown, info: { offset: { x: number } }) => {
    if (info.offset.x > 80)       onSnooze(task.id, 60)
    else if (info.offset.x < -80) handleComplete()
  }

  return (
    <div className="relative">
      {/* Ghost action labels — visible during swipe, behind card */}
      <motion.div
        style={{ opacity: doneOpacity }}
        className="absolute inset-y-0 left-4 flex items-center pointer-events-none z-0"
      >
        <span className="text-soft-mint text-2xl font-bold">✓</span>
      </motion.div>
      <motion.div
        style={{ opacity: snoozeOpacity }}
        className="absolute inset-y-0 right-4 flex items-center pointer-events-none z-0"
      >
        <span className="text-muted-text text-2xl">💤</span>
      </motion.div>

      <motion.div
        drag="x"
        dragSnapToOrigin
        dragElastic={0.15}
        style={{ x, opacity: cardOpacity }}
        onDragEnd={handleDragEnd}
        initial={{ opacity: 0, y: 24, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -24, scale: 0.96 }}
        transition={{ type: 'spring', stiffness: 300, damping: 28 }}
        className={`
          relative z-10 w-full rounded-2xl p-7 shadow-2xl select-none cursor-grab active:cursor-grabbing
          ${isBreakingDown
            ? 'bg-[#1E2235] border-2 border-muted-amber/40'
            : task.is_big_rock
              ? 'bg-[#1E2235] border-2 border-muted-amber/30'
              : 'bg-[#1E2235] border border-slate-700/60'
          }
        `}
      >
        {/* Top row: source badge + energy + Big Rock pill */}
        <div className="flex items-center justify-between mb-6">
          <span className="text-muted-text text-xs tracking-wide uppercase">
            {SOURCE_LABELS[task.source] ?? task.source}
          </span>
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-text flex items-center gap-1">
              {energyBadge(task.energy_required).icon}
              <span>{energyBadge(task.energy_required).label}</span>
            </span>
            {task.is_big_rock && (
              <span className="text-xs font-semibold text-muted-amber border border-muted-amber/40
                               rounded-full px-3 py-0.5">
                Big Rock
              </span>
            )}
          </div>
        </div>

        {/* ── INVERTED HIERARCHY ────────────────────────────────────────── */}

        {/* Micro-step — largest, boldest: the ONE thing to do right now */}
        <motion.p
          key={microStep}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl font-bold text-off-white leading-tight mb-3"
        >
          {microStep}
        </motion.p>

        {/* Main task title — demoted to secondary context */}
        <p className="text-sm text-muted-text leading-readable mb-6">
          {task.title}
        </p>

        {/* ─────────────────────────────────────────────────────────────── */}

        {/* Steps 2 & 3 after breakdown */}
        <AnimatePresence>
          {subSteps.length > 1 && !isBreakingDown && (
            <motion.ol
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden mb-6 space-y-2"
            >
              {subSteps.slice(1).map((step, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-muted-text">
                  <span className="text-soft-mint font-semibold shrink-0">{i + 2}.</span>
                  {step}
                </li>
              ))}
            </motion.ol>
          )}
        </AnimatePresence>

        {/* AI atomizing skeleton */}
        <AnimatePresence>
          {isBreakingDown && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="mb-6"
            >
              <p className="text-muted-amber text-xs font-semibold mb-3 tracking-wide uppercase">
                Atomising task…
              </p>
              <BreakdownSkeleton />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Progress Ring + Done button side by side */}
        <div className="flex items-center gap-5 mb-5">
          <ProgressRing startTime={startTimeRef.current} />
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            onClick={handleComplete}
            disabled={isCompleting || isBreakingDown}
            className="flex-1 py-4 bg-soft-mint text-deep-slate font-semibold rounded-xl
                       text-base hover:brightness-105 transition-all
                       disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isCompleting ? 'Completing…' : '✓ Done'}
          </motion.button>
        </div>

        {/* Break Down — always shown until steps appear */}
        {!isBreakingDown && subSteps.length === 0 && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            onClick={handleBreakdown}
            className="w-full py-3 bg-muted-amber/15 text-muted-amber font-medium
                       rounded-xl text-sm hover:bg-muted-amber/25 transition-colors
                       border border-muted-amber/30"
          >
            🔨 Break it down
          </motion.button>
        )}

        {/* Swipe affordance hint */}
        <p className="text-center text-muted-text text-xs mt-4 opacity-40">
          ← done &nbsp;·&nbsp; snooze 1hr →
        </p>
      </motion.div>
    </div>
  )
}

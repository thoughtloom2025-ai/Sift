# Sift UI Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Surgically replace EnergySlider, TaskCard, and FocusPage visuals with a neuroinclusive, anxiety-reducing UI while leaving all hooks, services, auth, and routing untouched.

**Architecture:** Option A — surgical component swap. All data logic stays in existing hooks (`useTasks`, `useEnergy`, `useFreshStart`). Only visual components change. No backend changes.

**Tech Stack:** React 18, TypeScript, Framer Motion 11, Tailwind CSS 3, lucide-react. No test framework installed — verification is `tsc --noEmit` + `vite build` + visual browser check.

---

## Task 1: Update Design Tokens

**Files:**
- Modify: `frontend/tailwind.config.js`
- Modify: `frontend/src/index.css`

**Step 1: Update tailwind.config.js color palette**

Replace the entire `colors` block in `tailwind.config.js`:

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'deep-slate': '#1A1C2E',
        'cloud-gray': '#CBD5E1',
        'soft-mint': '#B2D8C8',
        'muted-amber': '#E2B07E',
        'off-white': '#F8FAFC',
        'muted-text': '#94A3B8',
        'focus-slate': '#1E2235',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      lineHeight: {
        'readable': '1.6',
      },
    },
  },
  plugins: [],
}
```

**Step 2: Update index.css base styles**

Replace `index.css` entirely:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  box-sizing: border-box;
}

body {
  background-color: #1A1C2E;
  color: #F8FAFC;
  font-family: 'Inter', system-ui, sans-serif;
  line-height: 1.6;
  margin: 0;
  padding: 0;
}

::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: #1A1C2E;
}
::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 3px;
}

@keyframes breathe {
  0%, 100% { background-color: #1A1C2E; }
  50%       { background-color: #1E2235; }
}
```

**Step 3: Type-check**

```bash
cd frontend && npx tsc --noEmit
```
Expected: no errors (token names unchanged, only hex values differ)

**Step 4: Commit**

```bash
git add frontend/tailwind.config.js frontend/src/index.css
git commit -m "feat: update design tokens to neuroinclusive palette"
```

---

## Task 2: Build EnergyGate Component

**Files:**
- Create: `frontend/src/components/EnergyGate/EnergyGate.tsx`

**Step 1: Create the component file**

```tsx
// frontend/src/components/EnergyGate/EnergyGate.tsx
import { useState } from 'react'
import { motion } from 'framer-motion'

interface EnergyOption {
  icon: string
  label: string
  sublabel: string
  value: number
}

const OPTIONS: EnergyOption[] = [
  { icon: '🌊', label: 'Low',  sublabel: 'Gentle tasks only',         value: 2 },
  { icon: '⚡', label: 'Mid',  sublabel: 'Steady and present',        value: 3 },
  { icon: '🔥', label: 'High', sublabel: 'Ready to tackle anything',  value: 5 },
]

interface EnergyGateProps {
  onConfirm: (value: number) => Promise<void>
  isSubmitting: boolean
}

export function EnergyGate({ onConfirm, isSubmitting }: EnergyGateProps) {
  const [selected, setSelected] = useState<number | null>(null)

  const handleConfirm = async () => {
    if (selected === null) return
    await onConfirm(selected)
  }

  return (
    <motion.div
      key="energy-gate"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -40 }}
      transition={{ type: 'spring', stiffness: 260, damping: 28 }}
      className="w-full max-w-md mx-auto text-center"
    >
      <h1 className="text-4xl font-bold text-off-white mb-2 leading-readable">
        How's your bandwidth?
      </h1>
      <p className="text-muted-text mb-10">
        Be honest. Sift will match tasks to your energy.
      </p>

      {/* Three energy cards */}
      <div className="flex flex-col sm:flex-row gap-4 mb-10">
        {OPTIONS.map((opt) => {
          const isSelected = selected === opt.value
          return (
            <motion.button
              key={opt.value}
              onClick={() => setSelected(opt.value)}
              disabled={isSubmitting}
              animate={{
                scale: isSelected ? 1.05 : 1,
                opacity: selected !== null && !isSelected ? 0.45 : 1,
              }}
              whileTap={{ scale: 0.97 }}
              transition={{ type: 'spring', stiffness: 400, damping: 25 }}
              className={`
                flex-1 flex flex-col items-center justify-center gap-2
                py-9 px-4 rounded-2xl border-2 cursor-pointer
                transition-colors duration-150 select-none
                ${isSelected
                  ? 'border-soft-mint bg-soft-mint/10 shadow-lg shadow-soft-mint/20'
                  : 'border-slate-700 bg-slate-800/60 hover:border-slate-500'
                }
              `}
            >
              <span className="text-4xl">{opt.icon}</span>
              <span className="text-off-white font-semibold text-lg">{opt.label}</span>
              <span className="text-muted-text text-sm">{opt.sublabel}</span>
            </motion.button>
          )
        })}
      </div>

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.97 }}
        onClick={handleConfirm}
        disabled={selected === null || isSubmitting}
        className="w-full py-4 bg-soft-mint text-deep-slate font-semibold rounded-xl
                   text-lg hover:brightness-105 transition-all
                   disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {isSubmitting ? 'Loading…' : "Let's Focus →"}
      </motion.button>
    </motion.div>
  )
}
```

**Step 2: Type-check**

```bash
cd frontend && npx tsc --noEmit
```
Expected: no errors

**Step 3: Commit**

```bash
git add frontend/src/components/EnergyGate/EnergyGate.tsx
git commit -m "feat: add EnergyGate 3-card energy selector component"
```

---

## Task 3: Rebuild TaskCard

**Files:**
- Modify: `frontend/src/components/TaskCard/TaskCard.tsx`

This is the biggest visual change. The props interface stays identical so FocusPage needs no changes yet.

**Step 1: Replace TaskCard.tsx entirely**

```tsx
// frontend/src/components/TaskCard/TaskCard.tsx
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

function ProgressRing({ startTime }: { startTime: number }) {
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    const id = setInterval(() => {
      setElapsed(Date.now() - startTime)
    }, 10_000) // update every 10s — no ticking digits, just visual drift
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
        {/* Fill */}
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
  const [isCompleting, setIsCompleting]   = useState(false)
  const [isBreakingDown, setIsBreakingDown] = useState(false)
  const [subSteps, setSubSteps]           = useState<string[]>(task.sub_steps ?? [])
  const startTimeRef                       = useRef(Date.now())

  // Auto-snooze when ring completes
  useEffect(() => {
    const timer = setTimeout(() => {
      onSnooze(task.id, 60)
    }, SNOOZE_MS)
    return () => clearTimeout(timer)
  }, [task.id, onSnooze])

  // Reset sub-steps when task changes
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

  // Inverted hierarchy: micro-step is the star
  const microStep = subSteps.length > 0 ? subSteps[0] : `Begin: ${task.title}`

  // Swipe gesture values
  const x = useMotionValue(0)
  const snoozeOpacity = useTransform(x, [0, 80],  [0, 1])
  const doneOpacity   = useTransform(x, [-80, 0], [1, 0])
  const cardOpacity   = useTransform(x, [-120, -80, 0, 80, 120], [0.6, 1, 1, 1, 0.6])

  const handleDragEnd = (_: unknown, info: { offset: { x: number } }) => {
    if (info.offset.x > 80)        onSnooze(task.id, 60)
    else if (info.offset.x < -80)  handleComplete()
  }

  return (
    <div className="relative">
      {/* Swipe hint labels — behind the card */}
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
            ? 'bg-muted-amber/10 border-2 border-muted-amber/40'
            : task.is_big_rock
              ? 'bg-[#1E2235] border-2 border-muted-amber/30'
              : 'bg-[#1E2235] border border-slate-700/60'
          }
        `}
      >
        {/* Top row: source + big rock badge */}
        <div className="flex items-center justify-between mb-6">
          <span className="text-muted-text text-xs tracking-wide uppercase">
            {SOURCE_LABELS[task.source] ?? task.source}
          </span>
          {task.is_big_rock && (
            <span className="text-xs font-semibold text-muted-amber border border-muted-amber/40
                             rounded-full px-3 py-0.5">
              Big Rock
            </span>
          )}
        </div>

        {/* INVERTED HIERARCHY */}
        {/* Micro-step — largest, boldest */}
        <motion.p
          key={microStep}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl font-bold text-off-white leading-tight mb-3"
        >
          {microStep}
        </motion.p>

        {/* Main task title — demoted */}
        <p className="text-sm text-muted-text leading-readable mb-6">
          {task.title}
        </p>

        {/* Sub-steps (steps 2 & 3 after breakdown) */}
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

        {/* Breakdown skeleton */}
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

        {/* Progress Ring + Complete button */}
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

        {/* Break Down button — always visible */}
        {!isBreakingDown && subSteps.length === 0 && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            onClick={handleBreakdown}
            className="w-full py-3 bg-muted-amber/15 text-muted-amber font-medium
                       rounded-xl text-sm hover:bg-muted-amber/25 transition-colors border
                       border-muted-amber/30"
          >
            🔨 Break it down
          </motion.button>
        )}

        {/* Swipe hint */}
        <p className="text-center text-muted-text text-xs mt-4 opacity-50">
          ← done &nbsp;·&nbsp; snooze 1hr →
        </p>
      </motion.div>
    </div>
  )
}
```

**Step 2: Type-check**

```bash
cd frontend && npx tsc --noEmit
```
Expected: no errors

**Step 3: Commit**

```bash
git add frontend/src/components/TaskCard/TaskCard.tsx
git commit -m "feat: rebuild TaskCard with inverted hierarchy, progress ring, swipe gestures"
```

---

## Task 4: Update FocusPage — EnergyGate + Breathing Focus Mode

**Files:**
- Modify: `frontend/src/pages/FocusPage.tsx`

**Step 1: Replace FocusPage.tsx**

```tsx
// frontend/src/pages/FocusPage.tsx
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

  // Enter FOCUS_MODE once a task appears
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

  // ── FOCUS MODE: full-screen breathing, no nav ──────────────────────────────
  if (appState === 'FOCUS_MODE' && task) {
    return (
      <motion.div
        animate={{ backgroundColor: ['#1A1C2E', '#1E2235', '#1A1C2E'] }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
        className="min-h-screen flex flex-col items-center justify-center px-4 py-12"
        onClick={handleExitFocusMode}
      >
        {/* Tap anywhere to exit hint */}
        <p className="text-muted-text text-xs mb-8 opacity-40 select-none">
          tap anywhere to exit focus mode
        </p>

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

  // ── ENERGY GATE ────────────────────────────────────────────────────────────
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

  // ── FOCUSED (task visible, nav visible) ────────────────────────────────────
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
```

**Step 2: Type-check**

```bash
cd frontend && npx tsc --noEmit
```
Expected: no errors. If `CheckInPage` is imported anywhere, verify it still resolves (it redirects to /focus in App.tsx already).

**Step 3: Commit**

```bash
git add frontend/src/pages/FocusPage.tsx
git commit -m "feat: FocusPage state machine with EnergyGate + breathing focus mode"
```

---

## Task 5: Polish FreshStartPage

**Files:**
- Modify: `frontend/src/pages/FreshStartPage.tsx`

**Step 1: Replace FreshStartPage.tsx**

```tsx
// frontend/src/pages/FreshStartPage.tsx
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
          className="text-soft-mint text-lg"
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
            {/* No emoji — calm, grounded copy */}
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
```

**Step 2: Type-check**

```bash
cd frontend && npx tsc --noEmit
```
Expected: no errors

**Step 3: Commit**

```bash
git add frontend/src/pages/FreshStartPage.tsx
git commit -m "feat: polish FreshStartPage — calm copy, no red, guilt-free framing"
```

---

## Task 6: Final Build Verification

**Step 1: Full TypeScript check + build**

```bash
cd frontend && npx tsc --noEmit && npm run build
```
Expected: no TypeScript errors, build succeeds with no warnings about missing modules.

**Step 2: Lint**

```bash
cd frontend && npm run lint
```
Expected: 0 errors, 0 warnings

**Step 3: Docker rebuild**

```bash
cd /home/ubuntu/Projects/Sift && sudo docker compose build frontend
sudo docker compose up -d
```
Expected: build succeeds, container starts, `http://localhost:5174` serves the app.

**Step 4: Visual checklist in browser**

- [ ] Energy Gate shows 3 large cards (Low/Mid/High), no slider
- [ ] Selecting a card scales it up + glows Soft Mint, others dim
- [ ] Confirm button springs to task card
- [ ] TaskCard shows micro-step as largest text
- [ ] Progress ring animates slowly (no digits)
- [ ] Swipe right = snooze hint appears, swipe left = ✓ hint appears
- [ ] "Break it down" triggers amber pulse skeleton → 3 steps
- [ ] After 2s on task, background enters breathing mode
- [ ] Tapping breathing bg exits focus mode
- [ ] FreshStart has calm copy, no red, "Clear & Begin" button

**Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete neuroinclusive UI redesign — EnergyGate, TaskCard, FocusMode, FreshStart"
```

---

## Files Changed Summary

| File | Change |
|------|--------|
| `frontend/tailwind.config.js` | New design tokens (`#1A1C2E`, `#B2D8C8`, `#E2B07E`, `focus-slate`) |
| `frontend/src/index.css` | Updated base bg, breathe keyframe |
| `frontend/src/components/EnergyGate/EnergyGate.tsx` | New component (3-card gate) |
| `frontend/src/components/TaskCard/TaskCard.tsx` | Inverted hierarchy, progress ring, swipe, atomizing breakdown |
| `frontend/src/pages/FocusPage.tsx` | State machine, EnergyGate integration, breathing focus mode |
| `frontend/src/pages/FreshStartPage.tsx` | Calm copy, no red, guilt-free framing |

## Files NOT Changed

`useTasks.ts`, `useEnergy.ts`, `useFreshStart.ts`, `useIntegrations.ts`, `api.ts`, `taskService.ts`, `energyService.ts`, `AuthContext.tsx`, `ProtectedRoute.tsx`, `AppLayout.tsx`, `App.tsx`, `types/index.ts` — zero changes.

import { useState } from 'react'
import { motion } from 'framer-motion'

interface EnergyOption {
  icon: string
  label: string
  sublabel: string
  value: number
}

const OPTIONS: EnergyOption[] = [
  { icon: '🌊', label: 'Low',  sublabel: 'Gentle tasks only',        value: 2 },
  { icon: '⚡', label: 'Mid',  sublabel: 'Steady and present',       value: 3 },
  { icon: '🔥', label: 'High', sublabel: 'Ready to tackle anything', value: 5 },
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

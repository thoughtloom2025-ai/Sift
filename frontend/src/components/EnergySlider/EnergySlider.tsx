import { motion } from 'framer-motion'

interface EnergySliderProps {
  value: number
  onChange: (value: number) => void
  disabled?: boolean
}

const labels = ['', 'Drained', 'Low', 'Medium', 'High', 'Energized']

export function EnergySlider({ value, onChange, disabled }: EnergySliderProps) {
  return (
    <div className="w-full max-w-md">
      <div className="flex justify-between mb-3">
        {[1, 2, 3, 4, 5].map((level) => (
          <button
            key={level}
            onClick={() => !disabled && onChange(level)}
            disabled={disabled}
            className={`w-12 h-12 rounded-full font-semibold text-sm transition-all duration-200 ${
              value === level
                ? 'bg-soft-mint text-deep-slate scale-110 shadow-lg shadow-soft-mint/30'
                : 'bg-slate-800 text-muted-text hover:bg-slate-700'
            } disabled:cursor-not-allowed`}
          >
            {level}
          </button>
        ))}
      </div>

      <div className="relative h-2 bg-slate-800 rounded-full mt-4">
        <motion.div
          className="absolute top-0 left-0 h-full rounded-full"
          style={{ background: 'linear-gradient(to right, #94A3B8, #4ECCA3)' }}
          animate={{ width: `${((value - 1) / 4) * 100}%` }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        />
        {value > 0 && (
          <motion.div
            className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-soft-mint rounded-full shadow-lg shadow-soft-mint/50"
            animate={{ left: `calc(${((value - 1) / 4) * 100}% - 8px)` }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          />
        )}
      </div>

      <div className="text-center mt-4">
        <motion.span
          key={value}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-soft-mint font-medium"
        >
          {labels[value]}
        </motion.span>
      </div>
    </div>
  )
}

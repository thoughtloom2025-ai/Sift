import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface AddTaskModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (title: string, description?: string) => Promise<void>
}

export function AddTaskModal({ isOpen, onClose, onSubmit }: AddTaskModalProps) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const titleRef = useRef<HTMLInputElement>(null)

  // Autofocus title when modal opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => titleRef.current?.focus(), 50)
    } else {
      setTitle('')
      setDescription('')
      setError(null)
    }
  }, [isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return
    setIsSubmitting(true)
    setError(null)
    try {
      await onSubmit(title.trim(), description.trim() || undefined)
      onClose()
    } catch {
      setError('Failed to add task. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  // Close on Escape key
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    if (isOpen) window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-deep-slate/80 z-40 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 40 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed bottom-0 left-0 right-0 z-50 px-4 pb-8 sm:bottom-auto sm:top-1/2 sm:-translate-y-1/2 sm:max-w-lg sm:mx-auto"
          >
            <form
              onSubmit={handleSubmit}
              className="bg-cloud-gray rounded-2xl p-6 shadow-2xl"
            >
              <h2 className="text-deep-slate font-bold text-lg mb-1">Add a task</h2>
              <p className="text-slate-500 text-sm mb-4">
                Sift will figure out the priority automatically.
              </p>

              <input
                ref={titleRef}
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="What needs doing?"
                required
                className="w-full bg-white/70 text-deep-slate placeholder-slate-400
                           rounded-xl px-4 py-3 mb-3 outline-none
                           focus:ring-2 focus:ring-soft-mint transition-all"
              />

              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Optional — helps Sift rank it better"
                rows={3}
                className="w-full bg-white/70 text-deep-slate placeholder-slate-400
                           rounded-xl px-4 py-3 mb-4 outline-none resize-none
                           focus:ring-2 focus:ring-soft-mint transition-all"
              />

              {error && (
                <p className="text-muted-amber text-sm mb-3">{error}</p>
              )}

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 py-3 rounded-xl text-slate-500 font-medium
                             hover:bg-slate-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!title.trim() || isSubmitting}
                  className="flex-1 py-3 rounded-xl bg-soft-mint text-deep-slate font-semibold
                             hover:brightness-105 transition-all
                             disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? 'Adding…' : 'Add Task'}
                </button>
              </div>
            </form>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

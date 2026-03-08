import { useState, useCallback } from 'react'
import { energyService } from '../services/energyService'

export function useEnergy() {
  const [energyLevel, setEnergyLevel] = useState(3)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const submitEnergy = useCallback(async (level: number) => {
    setIsSubmitting(true)
    try {
      await energyService.log(level)
      setEnergyLevel(level)
      return true
    } catch {
      return false
    } finally {
      setIsSubmitting(false)
    }
  }, [])

  return { energyLevel, setEnergyLevel, submitEnergy, isSubmitting }
}

import { useState, useEffect } from 'react'
import { api } from '../services/api'
import type { FreshStartCheck, FreshStartReset } from '../types'

export function useFreshStart() {
  const [freshStartData, setFreshStartData] = useState<FreshStartCheck | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const check = async () => {
      try {
        const response = await api.get('/freshstart/check')
        setFreshStartData(response.data)
      } catch {
        // ignore
      } finally {
        setIsLoading(false)
      }
    }
    check()
  }, [])

  const triggerReset = async (): Promise<FreshStartReset> => {
    const response = await api.post('/freshstart/reset')
    return response.data
  }

  return { freshStartData, isLoading, triggerReset }
}

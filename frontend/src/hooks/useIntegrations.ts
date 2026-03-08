import { useState, useEffect, useCallback } from 'react'
import { integrationService } from '../services/integrationService'
import type { Integration } from '../types'

export function useIntegrations() {
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSyncing, setIsSyncing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchIntegrations = useCallback(async () => {
    try {
      const data = await integrationService.list()
      setIntegrations(data)
    } catch {
      setError('Failed to load integrations')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => { fetchIntegrations() }, [fetchIntegrations])

  const disconnect = useCallback(async (id: number) => {
    try {
      await integrationService.disconnect(id)
      await fetchIntegrations()
    } catch {
      setError('Failed to disconnect integration')
    }
  }, [fetchIntegrations])

  const syncAll = useCallback(async () => {
    setIsSyncing(true)
    setError(null)
    try {
      await integrationService.syncAll()
      await fetchIntegrations()
    } catch {
      setError('Sync failed. Please try again.')
    } finally {
      setIsSyncing(false)
    }
  }, [fetchIntegrations])

  return { integrations, isLoading, isSyncing, error, setError, disconnect, syncAll, fetchIntegrations }
}

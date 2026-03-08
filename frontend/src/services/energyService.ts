import { api } from './api'
import type { EnergyLog } from '../types'

export const energyService = {
  log: async (level: number): Promise<EnergyLog> => {
    const response = await api.post('/energy', { level })
    return response.data
  },
  getToday: async (): Promise<EnergyLog[]> => {
    const response = await api.get('/energy/today')
    return response.data
  },
}

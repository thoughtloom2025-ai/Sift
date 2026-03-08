import { api } from './api'
import type { Integration } from '../types'

export const integrationService = {
  list: async (): Promise<Integration[]> => {
    const response = await api.get('/integrations')
    return response.data
  },
  disconnect: async (integrationId: number): Promise<void> => {
    await api.delete(`/integrations/${integrationId}`)
  },
  syncAll: async (): Promise<void> => {
    await api.post('/integrations/sync')
  },
  getGmailAuthUrl: async (): Promise<string> => {
    const response = await api.get('/integrations/auth/gmail')
    return response.data.url
  },
  getSlackAuthUrl: async (): Promise<string> => {
    const response = await api.get('/integrations/auth/slack')
    return response.data.url
  },
  getNotionAuthUrl: async (): Promise<string> => {
    const response = await api.get('/integrations/auth/notion')
    return response.data.url
  },
}

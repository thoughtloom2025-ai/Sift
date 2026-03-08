import { api } from './api'
import type { Task } from '../types'

export const taskService = {
  getNext: async (energyLevel: number): Promise<Task | null> => {
    const response = await api.get(`/tasks/next?energy_level=${energyLevel}`)
    return response.data
  },
  getEligible: async (energyLevel: number): Promise<Task[]> => {
    const response = await api.get(`/tasks/eligible?energy_level=${energyLevel}`)
    return response.data
  },
  complete: async (taskId: number): Promise<Task> => {
    const response = await api.post(`/tasks/${taskId}/complete`)
    return response.data
  },
  snooze: async (taskId: number, snoozeDuration: number): Promise<Task> => {
    const response = await api.post(`/tasks/${taskId}/snooze`, { snooze_duration: snoozeDuration })
    return response.data
  },
  breakdown: async (taskId: number): Promise<string[]> => {
    const response = await api.post(`/tasks/${taskId}/breakdown`)
    return response.data.sub_steps
  },
  create: async (data: { title: string; description?: string; impact?: number; urgency?: number; energy_required?: number }): Promise<Task> => {
    const response = await api.post('/tasks', data)
    return response.data
  },
  list: async (status?: string): Promise<Task[]> => {
    const params = status ? `?status=${status}` : ''
    const response = await api.get(`/tasks${params}`)
    return response.data
  },
}

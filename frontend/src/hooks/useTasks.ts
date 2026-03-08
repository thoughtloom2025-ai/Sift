import { useState, useCallback } from 'react'
import { taskService } from '../services/taskService'
import type { Task } from '../types'

export function useTasks(energyLevel: number) {
  const [task, setTask] = useState<Task | null>(null)
  const [eligibleTasks, setEligibleTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchNext = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const next = await taskService.getNext(energyLevel)
      setTask(next)
    } catch {
      setError('Failed to load task')
    } finally {
      setIsLoading(false)
    }
  }, [energyLevel])

  const fetchEligible = useCallback(async () => {
    try {
      const tasks = await taskService.getEligible(energyLevel)
      setEligibleTasks(tasks)
    } catch {
      // non-critical, silently ignore
    }
  }, [energyLevel])

  const selectTask = useCallback((selected: Task) => {
    setTask(selected)
  }, [])

  const completeTask = useCallback(async (taskId: number) => {
    try {
      await taskService.complete(taskId)
      await fetchNext()
      await fetchEligible()
    } catch {
      setError('Failed to complete task')
    }
  }, [fetchNext, fetchEligible])

  const snoozeTask = useCallback(async (taskId: number, duration: number) => {
    try {
      await taskService.snooze(taskId, duration)
      await fetchNext()
      await fetchEligible()
    } catch {
      setError('Failed to snooze task')
    }
  }, [fetchNext, fetchEligible])

  const breakdownTask = useCallback(async (taskId: number): Promise<string[]> => {
    const steps = await taskService.breakdown(taskId)
    if (task && task.id === taskId) {
      setTask({ ...task, sub_steps: steps })
    }
    return steps
  }, [task])

  const createTask = useCallback(async (title: string, description?: string): Promise<void> => {
    await taskService.create({ title, description })
  }, [])

  return {
    task,
    eligibleTasks,
    isLoading,
    error,
    fetchNext,
    fetchEligible,
    selectTask,
    completeTask,
    snoozeTask,
    breakdownTask,
    createTask,
  }
}

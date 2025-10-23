import axios from 'axios'
import type { Athlete, AthleteInput, TrainingSession, TrainingSessionInput, TrainingSessionListResponse, Statistics } from './types'

const api = axios.create({
  baseURL: '/v1',
})

export const trainingApi = {
  // Athletes
  getAthletes: async () => {
    const response = await api.get<Athlete[]>('/athletes')
    return response.data
  },

  createAthlete: async (data: AthleteInput) => {
    const response = await api.post<Athlete>('/athletes', data)
    return response.data
  },

  updateAthlete: async (id: string, data: AthleteInput) => {
    const response = await api.put<Athlete>(`/athletes/${id}`, data)
    return response.data
  },

  deleteAthlete: async (id: string, cascade = false) => {
    await api.delete(`/athletes/${id}`, { params: { cascade } })
  },

  getAthleteStatistics: async (id: string) => {
    const response = await api.get<Statistics>(`/athletes/${id}/statistics`)
    return response.data
  },

  // Training Sessions
  getSessions: async (params?: { startDate?: string; endDate?: string; athleteId?: string; limit?: number; offset?: number }) => {
    const response = await api.get<TrainingSessionListResponse>('/training-sessions', { params })
    return response.data
  },

  getSession: async (id: string) => {
    const response = await api.get<TrainingSession>(`/training-sessions/${id}`)
    return response.data
  },

  createSession: async (data: TrainingSessionInput) => {
    const response = await api.post<TrainingSession>('/training-sessions', data)
    return response.data
  },

  updateSession: async (id: string, data: TrainingSessionInput) => {
    const response = await api.put<TrainingSession>(`/training-sessions/${id}`, data)
    return response.data
  },

  deleteSession: async (id: string) => {
    await api.delete(`/training-sessions/${id}`)
  },

  getStatistics: async (params?: { startDate?: string; endDate?: string }) => {
    const response = await api.get<Statistics>('/training-sessions/statistics', { params })
    return response.data
  },
}

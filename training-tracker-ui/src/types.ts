export interface Athlete {
  id: string
  name: string
}

export interface AthleteInput {
  name: string
}

export interface TrainingSession {
  id: string
  athlete_id: string
  athlete_name: string
  date: string
  duration: number
  distance: number
  notes: string | null
  createdAt: string
  updatedAt: string
}

export interface TrainingSessionInput {
  athlete_id: string
  date: string
  duration: number
  distance: number
  notes?: string
}

export interface Statistics {
  totalSessions: number
  totalDuration: number
  totalDistance: number
  averageDuration: number
  averageDistance: number
  averagePace: number
}

export interface Pagination {
  total: number
  limit: number
  offset: number
  hasMore: boolean
}

export interface TrainingSessionListResponse {
  data: TrainingSession[]
  pagination: Pagination
}

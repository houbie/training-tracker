import { useState, useEffect } from 'react'
import { trainingApi } from './api'
import type { Athlete, TrainingSession, Statistics } from './types'
import SessionList from './components/SessionList'
import SessionForm from './components/SessionForm'
import StatisticsCard from './components/StatisticsCard'
import AthleteManagement from './components/AthleteManagement'
import AthleteProfile from './components/AthleteProfile'

function App() {
  const [athletes, setAthletes] = useState<Athlete[]>([])
  const [sessions, setSessions] = useState<TrainingSession[]>([])
  const [statistics, setStatistics] = useState<Statistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [editingSession, setEditingSession] = useState<TrainingSession | null>(null)
  const [selectedAthleteId, setSelectedAthleteId] = useState<string>('')
  const [viewingAthlete, setViewingAthlete] = useState<Athlete | null>(null)
  const [showAthleteManagement, setShowAthleteManagement] = useState(false)

  const loadData = async () => {
    try {
      setLoading(true)
      const [athletesData, sessionsData, statsData] = await Promise.all([
        trainingApi.getAthletes(),
        trainingApi.getSessions({ athleteId: selectedAthleteId || undefined }),
        trainingApi.getStatistics(),
      ])
      setAthletes(athletesData)
      setSessions(sessionsData.data)
      setStatistics(statsData)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAthleteFilterChange = (athleteId: string) => {
    setSelectedAthleteId(athleteId)
  }

  const handleViewAthleteProfile = (athlete: Athlete) => {
    setViewingAthlete(athlete)
  }

  useEffect(() => {
    loadData()
  }, [selectedAthleteId])

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this session?')) return

    try {
      await trainingApi.deleteSession(id)
      await loadData()
    } catch (error) {
      console.error('Error deleting session:', error)
      alert('Failed to delete session')
    }
  }

  const handleEdit = (session: TrainingSession) => {
    setEditingSession(session)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleFormSuccess = async () => {
    setEditingSession(null)
    await loadData()
  }

  const handleCancelEdit = () => {
    setEditingSession(null)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <h1 className="text-4xl font-bold">🏃 Training Tracker</h1>
            <button
              onClick={() => setShowAthleteManagement(!showAthleteManagement)}
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded transition"
            >
              {showAthleteManagement ? 'Hide' : 'Manage'} Athletes
            </button>
          </div>
          <p className="text-gray-400">Track your training sessions and monitor your progress</p>
        </header>

        {showAthleteManagement && (
          <div className="mb-8">
            <AthleteManagement athletes={athletes} onUpdate={loadData} />
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          <div className="lg:col-span-2">
            <SessionForm
              athletes={athletes}
              editingSession={editingSession}
              onSuccess={handleFormSuccess}
              onCancel={handleCancelEdit}
            />
          </div>

          <div>
            <StatisticsCard statistics={statistics} />
          </div>
        </div>

        <div className="mb-4">
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3">Quick Links</h3>
            <div className="flex flex-wrap gap-2">
              {athletes.map((athlete) => (
                <button
                  key={athlete.id}
                  onClick={() => handleViewAthleteProfile(athlete)}
                  className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded transition"
                >
                  📊 {athlete.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        <SessionList
          sessions={sessions}
          athletes={athletes}
          onDelete={handleDelete}
          onEdit={handleEdit}
          selectedAthleteId={selectedAthleteId}
          onAthleteFilterChange={handleAthleteFilterChange}
        />

        {viewingAthlete && (
          <AthleteProfile
            athlete={viewingAthlete}
            onClose={() => setViewingAthlete(null)}
            onEditSession={handleEdit}
          />
        )}
      </div>
    </div>
  )
}

export default App

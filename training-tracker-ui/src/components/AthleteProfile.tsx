import { useState, useEffect } from 'react'
import type { Athlete, TrainingSession, Statistics } from '../types'
import { trainingApi } from '../api'

interface AthleteProfileProps {
  athlete: Athlete
  onClose: () => void
  onEditSession: (session: TrainingSession) => void
}

export default function AthleteProfile({ athlete, onClose, onEditSession }: AthleteProfileProps) {
  const [sessions, setSessions] = useState<TrainingSession[]>([])
  const [statistics, setStatistics] = useState<Statistics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAthleteData()
  }, [athlete.id])

  const loadAthleteData = async () => {
    try {
      setLoading(true)
      const [sessionsData, statsData] = await Promise.all([
        trainingApi.getSessions({ athleteId: athlete.id }),
        trainingApi.getAthleteStatistics(athlete.id),
      ])
      setSessions(sessionsData.data)
      setStatistics(statsData)
    } catch (error) {
      console.error('Error loading athlete data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteSession = async (id: string) => {
    if (!confirm('Are you sure you want to delete this session?')) return

    try {
      await trainingApi.deleteSession(id)
      await loadAthleteData()
    } catch (error) {
      console.error('Error deleting session:', error)
      alert('Failed to delete session')
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const calculatePace = (duration: number, distance: number) => {
    if (distance === 0) return 'N/A'
    return (duration / distance).toFixed(2)
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
        <div className="bg-gray-800 rounded-lg p-8 max-w-6xl w-full mx-4">
          <div className="text-white text-xl text-center">Loading...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 overflow-y-auto p-4">
      <div className="bg-gray-800 rounded-lg max-w-6xl w-full my-8">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-700 flex justify-between items-center">
          <h2 className="text-3xl font-bold">{athlete.name}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-3xl leading-none"
          >
            ×
          </button>
        </div>

        {/* Statistics */}
        {statistics && (
          <div className="p-6 border-b border-gray-700">
            <h3 className="text-xl font-semibold mb-4">Statistics</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="bg-gray-700 p-4 rounded">
                <div className="text-gray-400 text-sm">Total Sessions</div>
                <div className="text-2xl font-bold">{statistics.totalSessions}</div>
              </div>
              <div className="bg-gray-700 p-4 rounded">
                <div className="text-gray-400 text-sm">Total Distance</div>
                <div className="text-2xl font-bold">{statistics.totalDistance} km</div>
              </div>
              <div className="bg-gray-700 p-4 rounded">
                <div className="text-gray-400 text-sm">Total Duration</div>
                <div className="text-2xl font-bold">{statistics.totalDuration} min</div>
              </div>
              <div className="bg-gray-700 p-4 rounded">
                <div className="text-gray-400 text-sm">Avg Distance</div>
                <div className="text-2xl font-bold">{statistics.averageDistance} km</div>
              </div>
              <div className="bg-gray-700 p-4 rounded">
                <div className="text-gray-400 text-sm">Avg Duration</div>
                <div className="text-2xl font-bold">{statistics.averageDuration} min</div>
              </div>
              <div className="bg-gray-700 p-4 rounded">
                <div className="text-gray-400 text-sm">Avg Pace</div>
                <div className="text-2xl font-bold">{statistics.averagePace} min/km</div>
              </div>
            </div>
          </div>
        )}

        {/* Training History */}
        <div className="p-6">
          <h3 className="text-xl font-semibold mb-4">
            Training History ({sessions.length} sessions)
          </h3>

          {sessions.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              No training sessions yet
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-700">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Duration
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Distance
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Pace
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Notes
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {sessions.map((session) => (
                    <tr key={session.id} className="hover:bg-gray-750">
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="font-medium">{formatDate(session.date)}</div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="text-gray-300">{session.duration} min</div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="text-gray-300">{session.distance} km</div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="text-gray-300">
                          {calculatePace(session.duration, session.distance)} min/km
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-gray-400 max-w-xs truncate">
                          {session.notes || <span className="italic">No notes</span>}
                        </div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => {
                            onEditSession(session)
                            onClose()
                          }}
                          className="text-blue-400 hover:text-blue-300 mr-4"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteSession(session.id)}
                          className="text-red-400 hover:text-red-300"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-700 flex justify-end">
          <button
            onClick={onClose}
            className="bg-gray-600 hover:bg-gray-500 text-white px-6 py-2 rounded transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

import type { Athlete, TrainingSession } from '../types'

interface SessionListProps {
  sessions: TrainingSession[]
  athletes: Athlete[]
  onDelete: (id: string) => void
  onEdit: (session: TrainingSession) => void
  selectedAthleteId?: string
  onAthleteFilterChange: (athleteId: string) => void
}

export default function SessionList({
  sessions,
  athletes,
  onDelete,
  onEdit,
  selectedAthleteId = '',
  onAthleteFilterChange,
}: SessionListProps) {
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

  if (sessions.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-8 text-center">
        <p className="text-gray-400 text-lg">No training sessions yet. Add your first session above!</p>
      </div>
    )
  }

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-700">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Training Sessions</h2>
          <div className="flex items-center gap-2">
            <label htmlFor="athlete-filter" className="text-sm text-gray-400">
              Filter by athlete:
            </label>
            <select
              id="athlete-filter"
              value={selectedAthleteId}
              onChange={(e) => onAthleteFilterChange(e.target.value)}
              className="px-3 py-1 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            >
              <option value="">All Athletes</option>
              {athletes.map((athlete) => (
                <option key={athlete.id} value={athlete.id}>
                  {athlete.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-700">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Athlete
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Duration
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Distance
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Pace
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                Notes
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {sessions.map((session) => (
              <tr key={session.id} className="hover:bg-gray-750">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-gray-300">{session.athlete_name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="font-medium">{formatDate(session.date)}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-gray-300">{session.duration} min</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-gray-300">{session.distance} km</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-gray-300">{calculatePace(session.duration, session.distance)} min/km</div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-gray-400 max-w-xs truncate">
                    {session.notes || <span className="italic">No notes</span>}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => onEdit(session)}
                    className="text-blue-400 hover:text-blue-300 mr-4"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => onDelete(session.id)}
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
    </div>
  )
}

import type { Statistics } from '../types'

interface StatisticsCardProps {
  statistics: Statistics | null
}

export default function StatisticsCard({ statistics }: StatisticsCardProps) {
  if (!statistics) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">Statistics</h2>
        <p className="text-gray-400">Loading...</p>
      </div>
    )
  }

  const stats = [
    { label: 'Total Sessions', value: statistics.totalSessions, suffix: '' },
    { label: 'Total Duration', value: statistics.totalDuration.toFixed(1), suffix: ' min' },
    { label: 'Total Distance', value: statistics.totalDistance.toFixed(1), suffix: ' km' },
    { label: 'Avg Duration', value: statistics.averageDuration.toFixed(1), suffix: ' min' },
    { label: 'Avg Distance', value: statistics.averageDistance.toFixed(1), suffix: ' km' },
    { label: 'Avg Pace', value: statistics.averagePace.toFixed(2), suffix: ' min/km' },
  ]

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-4">📊 Statistics</h2>

      <div className="space-y-4">
        {stats.map((stat) => (
          <div key={stat.label} className="border-b border-gray-700 pb-3 last:border-b-0">
            <div className="text-sm text-gray-400 mb-1">{stat.label}</div>
            <div className="text-2xl font-bold">
              {stat.value}
              <span className="text-base text-gray-400 font-normal">{stat.suffix}</span>
            </div>
          </div>
        ))}
      </div>

      {statistics.totalSessions === 0 && (
        <div className="mt-4 text-sm text-gray-400 italic">
          Add some training sessions to see statistics
        </div>
      )}
    </div>
  )
}

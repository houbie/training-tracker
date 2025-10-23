import { useState, useEffect } from 'react'
import { trainingApi } from '../api'
import type { Athlete, TrainingSession } from '../types'

interface SessionFormProps {
  athletes: Athlete[]
  editingSession: TrainingSession | null
  onSuccess: () => void
  onCancel: () => void
}

export default function SessionForm({ athletes, editingSession, onSuccess, onCancel }: SessionFormProps) {
  const [athleteId, setAthleteId] = useState('')
  const [date, setDate] = useState('')
  const [duration, setDuration] = useState('')
  const [distance, setDistance] = useState('')
  const [notes, setNotes] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (editingSession) {
      setAthleteId(editingSession.athlete_id)
      setDate(editingSession.date)
      setDuration(editingSession.duration.toString())
      setDistance(editingSession.distance.toString())
      setNotes(editingSession.notes || '')
    } else {
      resetForm()
    }
  }, [editingSession, athletes])

  const resetForm = () => {
    setAthleteId(athletes.length > 0 ? athletes[0].id : '')
    setDate(new Date().toISOString().split('T')[0])
    setDuration('')
    setDistance('')
    setNotes('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const data = {
      athlete_id: athleteId,
      date,
      duration: parseFloat(duration),
      distance: parseFloat(distance),
      notes: notes.trim() || undefined,
    }

    try {
      setSubmitting(true)
      if (editingSession) {
        await trainingApi.updateSession(editingSession.id, data)
      } else {
        await trainingApi.createSession(data)
      }
      resetForm()
      onSuccess()
    } catch (error) {
      console.error('Error saving session:', error)
      alert('Failed to save session')
    } finally {
      setSubmitting(false)
    }
  }

  const handleCancel = () => {
    resetForm()
    onCancel()
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-4">
        {editingSession ? 'Edit Session' : 'Add New Session'}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="athlete" className="block text-sm font-medium mb-1">
            Athlete
          </label>
          <select
            id="athlete"
            value={athleteId}
            onChange={(e) => setAthleteId(e.target.value)}
            required
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select an athlete</option>
            {athletes.map((athlete) => (
              <option key={athlete.id} value={athlete.id}>
                {athlete.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="date" className="block text-sm font-medium mb-1">
            Date
          </label>
          <input
            type="date"
            id="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="duration" className="block text-sm font-medium mb-1">
              Duration (minutes)
            </label>
            <input
              type="number"
              id="duration"
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
              step="0.1"
              min="0"
              required
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="distance" className="block text-sm font-medium mb-1">
              Distance (km)
            </label>
            <input
              type="number"
              id="distance"
              value={distance}
              onChange={(e) => setDistance(e.target.value)}
              step="0.1"
              min="0"
              required
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div>
          <label htmlFor="notes" className="block text-sm font-medium mb-1">
            Notes (optional)
          </label>
          <textarea
            id="notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            maxLength={1000}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Add any notes about your session..."
          />
        </div>

        <div className="flex gap-2">
          <button
            type="submit"
            disabled={submitting}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-4 py-2 rounded-md font-medium transition-colors"
          >
            {submitting ? 'Saving...' : editingSession ? 'Update Session' : 'Add Session'}
          </button>

          {editingSession && (
            <button
              type="button"
              onClick={handleCancel}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-md font-medium transition-colors"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  )
}

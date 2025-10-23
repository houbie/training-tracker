import { useState } from 'react'
import type { Athlete } from '../types'
import { trainingApi } from '../api'

interface AthleteManagementProps {
  athletes: Athlete[]
  onUpdate: () => void
}

export default function AthleteManagement({ athletes, onUpdate }: AthleteManagementProps) {
  const [isCreating, setIsCreating] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return

    setLoading(true)
    try {
      await trainingApi.createAthlete({ name: name.trim() })
      setName('')
      setIsCreating(false)
      await onUpdate()
    } catch (error) {
      console.error('Error creating athlete:', error)
      alert('Failed to create athlete')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdate = async (id: string) => {
    if (!name.trim()) return

    setLoading(true)
    try {
      await trainingApi.updateAthlete(id, { name: name.trim() })
      setName('')
      setEditingId(null)
      await onUpdate()
    } catch (error) {
      console.error('Error updating athlete:', error)
      alert('Failed to update athlete')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string, name: string) => {
    try {
      // First try without cascade
      await trainingApi.deleteAthlete(id, false)
      await onUpdate()
    } catch (error: any) {
      // If athlete has sessions, ask about cascade delete
      if (error.response?.data?.error === 'ATHLETE_HAS_SESSIONS') {
        const sessionCount = error.response.data.sessionCount
        const confirmCascade = confirm(
          `${name} has ${sessionCount} training session(s). Do you want to delete the athlete AND all their sessions?`
        )

        if (confirmCascade) {
          try {
            await trainingApi.deleteAthlete(id, true)
            await onUpdate()
          } catch (cascadeError) {
            console.error('Error deleting athlete with cascade:', cascadeError)
            alert('Failed to delete athlete')
          }
        }
      } else {
        console.error('Error deleting athlete:', error)
        alert('Failed to delete athlete')
      }
    }
  }

  const startEdit = (athlete: Athlete) => {
    setEditingId(athlete.id)
    setName(athlete.name)
    setIsCreating(false)
  }

  const cancelEdit = () => {
    setEditingId(null)
    setIsCreating(false)
    setName('')
  }

  return (
    <div className="bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Athletes</h2>
        {!isCreating && !editingId && (
          <button
            onClick={() => setIsCreating(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition"
          >
            + Add Athlete
          </button>
        )}
      </div>

      {/* Create/Edit Form */}
      {(isCreating || editingId) && (
        <form
          onSubmit={(e) => {
            e.preventDefault()
            if (editingId) {
              handleUpdate(editingId)
            } else {
              handleCreate(e)
            }
          }}
          className="mb-4 p-4 bg-gray-700 rounded"
        >
          <div className="flex gap-2">
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Athlete name"
              className="flex-1 px-3 py-2 bg-gray-600 rounded text-white"
              disabled={loading}
              autoFocus
            />
            <button
              type="submit"
              disabled={loading || !name.trim()}
              className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-4 py-2 rounded transition"
            >
              {loading ? 'Saving...' : editingId ? 'Update' : 'Create'}
            </button>
            <button
              type="button"
              onClick={cancelEdit}
              disabled={loading}
              className="bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded transition"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Athletes List */}
      <div className="space-y-2">
        {athletes.length === 0 ? (
          <p className="text-gray-400 text-center py-4">No athletes yet. Add your first athlete!</p>
        ) : (
          athletes.map((athlete) => (
            <div
              key={athlete.id}
              className="flex justify-between items-center p-3 bg-gray-700 rounded hover:bg-gray-650 transition"
            >
              <span className="text-lg">{athlete.name}</span>
              <div className="flex gap-2">
                <button
                  onClick={() => startEdit(athlete)}
                  disabled={loading || isCreating || editingId !== null}
                  className="text-blue-400 hover:text-blue-300 disabled:text-gray-500 transition"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(athlete.id, athlete.name)}
                  disabled={loading || isCreating || editingId !== null}
                  className="text-red-400 hover:text-red-300 disabled:text-gray-500 transition"
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

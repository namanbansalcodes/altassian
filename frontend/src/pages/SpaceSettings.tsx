import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Trash2 } from 'lucide-react'
import * as api from '../api'
import { toast, getErrorMessage } from '../lib/toast'
import { SettingsSkeleton } from '../components/Skeleton'

export default function SpaceSettings() {
  const { spaceKey } = useParams<{ spaceKey: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: space, isLoading } = useQuery({
    queryKey: ['space', spaceKey],
    queryFn: () => api.getSpace(spaceKey!),
    enabled: !!spaceKey,
  })

  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  useEffect(() => {
    if (space) {
      setName(space.name)
      setDescription(space.description || '')
    }
  }, [space])

  const updateMut = useMutation({
    mutationFn: () => api.updateSpace(spaceKey!, { name, description }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['spaces'] })
      queryClient.invalidateQueries({ queryKey: ['space', spaceKey] })
      toast.success('Settings saved')
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const deleteMut = useMutation({
    mutationFn: () => api.deleteSpace(spaceKey!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['spaces'] })
      toast.success('Space deleted')
      navigate('/spaces')
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  if (isLoading) return <SettingsSkeleton />
  if (!space) return <div className="text-center py-12 text-gray-500 dark:text-gray-400">Space not found</div>

  return (
    <div className="max-w-lg mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate(`/spaces/${spaceKey}`)} className="text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400">
          <ArrowLeft size={20} />
        </button>
        <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">Space Settings</h1>
      </div>

      <form onSubmit={e => { e.preventDefault(); updateMut.mutate() }} className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-4 sm:p-6 space-y-5 mb-6 form-mobile-spaced">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Space name</label>
          <input type="text" value={name} onChange={e => setName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Space key</label>
          <input type="text" value={space.key} disabled
            className="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 text-gray-500 dark:text-gray-400 font-mono" />
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">Space key cannot be changed</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
          <textarea value={description} onChange={e => setDescription(e.target.value)}
            rows={3} className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none" />
        </div>
        <div className="flex justify-end">
          <button type="submit" disabled={!name.trim() || updateMut.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">
            {updateMut.isPending ? 'Saving...' : 'Save changes'}
          </button>
        </div>
        {/* Success is shown via toast */}
      </form>

      <div className="bg-white dark:bg-gray-900 rounded-xl border border-red-200 dark:border-red-800 p-4 sm:p-6">
        <h3 className="text-lg font-semibold text-red-700 dark:text-red-400 mb-2">Danger Zone</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">Deleting a space will permanently remove all its pages and content.</p>
        <button onClick={() => { if (confirm(`Delete space "${space.name}"? This cannot be undone.`)) deleteMut.mutate() }}
          className="flex items-center gap-1.5 px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700">
          <Trash2 size={14} /> Delete space
        </button>
      </div>
    </div>
  )
}

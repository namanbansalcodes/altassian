import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '../api'
import { toast, getErrorMessage } from '../lib/toast'

export default function CreateSpace() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [key, setKey] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState('')

  const mutation = useMutation({
    mutationFn: () => api.createSpace({ name, key: key.toUpperCase(), description }),
    onSuccess: (space) => {
      queryClient.invalidateQueries({ queryKey: ['spaces'] })
      toast.success('Space created')
      navigate(`/spaces/${space.key}`)
    },
    onError: (err: any) => {
      const msg = getErrorMessage(err)
      setError(msg)
      toast.error(msg)
    },
  })

  const handleNameChange = (value: string) => {
    setName(value)
    if (!key || key === name.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 6)) {
      setKey(value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 6))
    }
  }

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">Create a Space</h1>
      <form onSubmit={e => { e.preventDefault(); mutation.mutate() }} className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-4 sm:p-6 space-y-5 form-mobile-spaced">
        {error && <div className="bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 text-sm p-3 rounded-lg">{error}</div>}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Space name</label>
          <input type="text" value={name} onChange={e => handleNameChange(e.target.value)}
            placeholder="e.g. Engineering"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Space key</label>
          <input type="text" value={key} onChange={e => setKey(e.target.value.toUpperCase())}
            placeholder="e.g. ENG" maxLength={10}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none font-mono" />
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">Unique identifier for URLs</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
          <textarea value={description} onChange={e => setDescription(e.target.value)}
            rows={3} placeholder="What is this space about?"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none" />
        </div>
        <div className="flex justify-end gap-3">
          <button type="button" onClick={() => navigate(-1)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg text-sm hover:bg-gray-50 dark:hover:bg-gray-800">
            Cancel
          </button>
          <button type="submit" disabled={!name.trim() || !key.trim() || mutation.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">
            {mutation.isPending ? 'Creating...' : 'Create space'}
          </button>
        </div>
      </form>
    </div>
  )
}

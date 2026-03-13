import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { BookOpen, Plus, Users } from 'lucide-react'
import * as api from '../api'
import { SpaceListSkeleton } from '../components/Skeleton'

export default function SpaceList() {
  const { data: spaces, isLoading } = useQuery({
    queryKey: ['spaces'],
    queryFn: api.getSpaces,
  })

  if (isLoading) return <SpaceListSkeleton />

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-3">
        <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">Spaces</h1>
        <Link to="/spaces/create"
          className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 shrink-0 self-start">
          <Plus size={16} /> Create space
        </Link>
      </div>

      {spaces?.length ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {spaces.map(space => (
            <Link key={space.id} to={`/spaces/${space.key}`}
              className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-4 sm:p-5 hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-sm transition-all">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-lg bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 flex items-center justify-center text-lg font-bold shrink-0">
                  {space.key.slice(0, 2)}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-800 dark:text-gray-200">{space.name}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-2">{space.description || 'No description'}</p>
                  <div className="flex items-center gap-3 mt-2 text-xs text-gray-400 dark:text-gray-500">
                    <span className="flex items-center gap-1"><Users size={12} /> {space.owner?.username}</span>
                    <span>{space.key}</span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-12 text-center">
          <BookOpen size={48} className="mx-auto mb-3 text-gray-300 dark:text-gray-600" />
          <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-1">No spaces yet</h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">Create your first space to start organizing knowledge</p>
          <Link to="/spaces/create"
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
            <Plus size={16} /> Create space
          </Link>
        </div>
      )}
    </div>
  )
}

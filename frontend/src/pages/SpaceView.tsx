import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { FileText, Plus, Settings } from 'lucide-react'
import * as api from '../api'
import { SpaceViewSkeleton } from '../components/Skeleton'

export default function SpaceView() {
  const { spaceKey } = useParams<{ spaceKey: string }>()

  const { data: space, isLoading: spaceLoading } = useQuery({
    queryKey: ['space', spaceKey],
    queryFn: () => api.getSpace(spaceKey!),
    enabled: !!spaceKey,
  })

  const { data: pages } = useQuery({
    queryKey: ['pages', spaceKey],
    queryFn: () => api.getPages(spaceKey!),
    enabled: !!spaceKey,
  })

  if (spaceLoading) return <SpaceViewSkeleton />
  if (!space) return <div className="text-center py-12 text-gray-500 dark:text-gray-400">Space not found</div>

  const rootPages = pages?.filter(p => !p.parent) || []

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-start justify-between mb-6 gap-3">
        <div className="flex items-center gap-3 sm:gap-4 min-w-0">
          <div className="w-11 h-11 sm:w-14 sm:h-14 rounded-xl bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 flex items-center justify-center text-lg sm:text-xl font-bold shrink-0">
            {space.key.slice(0, 2)}
          </div>
          <div className="min-w-0">
            <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100 truncate">{space.name}</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5 truncate">{space.description || 'No description'}</p>
          </div>
        </div>
        <div className="flex gap-2 shrink-0 flex-wrap">
          <Link to={`/spaces/${spaceKey}/pages/new`}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
            <Plus size={14} /> New page
          </Link>
          <Link to={`/spaces/${spaceKey}/settings`}
            className="flex items-center gap-1.5 px-3 py-1.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg text-sm hover:bg-gray-50 dark:hover:bg-gray-800">
            <Settings size={14} />
          </Link>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
          <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300">Pages</h2>
        </div>
        <div className="divide-y divide-gray-100 dark:divide-gray-800">
          {rootPages.map(page => (
            <PageRow key={page.id} page={page} spaceKey={spaceKey!} depth={0} />
          ))}
          {rootPages.length === 0 && (
            <div className="p-8 text-center text-gray-400 dark:text-gray-500">
              <FileText size={32} className="mx-auto mb-2 opacity-50" />
              <p>No pages yet</p>
              <Link to={`/spaces/${spaceKey}/pages/new`} className="text-blue-600 dark:text-blue-400 text-sm hover:underline mt-1 inline-block">
                Create your first page
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function PageRow({ page, spaceKey, depth }: { page: any; spaceKey: string; depth: number }) {
  return (
    <>
      <Link to={`/spaces/${spaceKey}/pages/${page.slug}`}
        className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800"
        style={{ paddingLeft: `${Math.min(depth * 12, 48) + 16}px` }}>
        <FileText size={16} className="text-blue-500 shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate">{page.title}</p>
          <p className="text-xs text-gray-400 dark:text-gray-500">
            {page.author?.first_name || page.author?.username} · {new Date(page.updated_at).toLocaleDateString()}
          </p>
        </div>
      </Link>
      {page.children?.map((child: any) => (
        <PageRow key={child.id} page={child} spaceKey={spaceKey} depth={depth + 1} />
      ))}
    </>
  )
}

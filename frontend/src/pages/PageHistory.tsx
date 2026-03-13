import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Clock, User, ChevronDown, ChevronUp } from 'lucide-react'
import * as api from '../api'
import { HistorySkeleton } from '../components/Skeleton'

export default function PageHistory() {
  const { spaceKey, pageSlug } = useParams<{ spaceKey: string; pageSlug: string }>()
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null)
  const [mobileListExpanded, setMobileListExpanded] = useState(true)

  const { data: versions, isLoading } = useQuery({
    queryKey: ['versions', spaceKey, pageSlug],
    queryFn: () => api.getPageVersions(spaceKey!, pageSlug!),
    enabled: !!spaceKey && !!pageSlug,
  })

  const { data: versionDetail } = useQuery({
    queryKey: ['version', spaceKey, pageSlug, selectedVersion],
    queryFn: () => api.getPageVersion(spaceKey!, pageSlug!, selectedVersion!),
    enabled: !!selectedVersion,
  })

  if (isLoading) return <HistorySkeleton />

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Link to={`/spaces/${spaceKey}/pages/${pageSlug}`} className="text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 p-1">
          <ArrowLeft size={20} />
        </Link>
        <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">Page History</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
        {/* Version list */}
        <div className="md:col-span-1 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <button
            onClick={() => setMobileListExpanded(!mobileListExpanded)}
            className="w-full p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 flex items-center justify-between md:cursor-default"
          >
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">Versions</h3>
            <span className="md:hidden text-gray-400">
              {mobileListExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </span>
          </button>
          <div className={`divide-y divide-gray-100 dark:divide-gray-800 max-h-[40vh] md:max-h-[600px] overflow-y-auto ${mobileListExpanded ? '' : 'hidden md:block'}`}>
            {versions?.map(v => (
              <button
                key={v.id}
                onClick={() => {
                  setSelectedVersion(v.id)
                  setMobileListExpanded(false)
                }}
                className={`w-full text-left p-3 hover:bg-gray-50 dark:hover:bg-gray-800 ${selectedVersion === v.id ? 'bg-blue-50 dark:bg-blue-900/30 border-l-2 border-blue-600' : ''}`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium text-gray-800 dark:text-gray-200">v{v.version_number}</span>
                  <span className="text-xs text-gray-400 dark:text-gray-500">{new Date(v.created_at).toLocaleDateString()}</span>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                  <User size={10} /> {v.author?.first_name || v.author?.username}
                </p>
                {v.change_message && (
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1 truncate">{v.change_message}</p>
                )}
              </button>
            ))}
            {(!versions || versions.length === 0) && (
              <p className="p-4 text-sm text-gray-400 dark:text-gray-500">No version history</p>
            )}
          </div>
        </div>

        {/* Version content */}
        <div className="md:col-span-2 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              {versionDetail ? `Version ${versionDetail.version_number} — ${versionDetail.title}` : 'Select a version'}
            </h3>
            {versionDetail && (
              <button
                onClick={() => setMobileListExpanded(true)}
                className="md:hidden text-xs text-blue-600 dark:text-blue-400 hover:underline"
              >
                Show versions
              </button>
            )}
          </div>
          {versionDetail ? (
            <div className="p-4 sm:p-6 prose prose-blue dark:prose-invert max-w-none prose-responsive" dangerouslySetInnerHTML={{ __html: versionDetail.content ?? '' }} />
          ) : (
            <div className="p-6 text-center text-gray-400 dark:text-gray-500">
              <Clock size={32} className="mx-auto mb-2 opacity-50" />
              <p>Select a version to view its content</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

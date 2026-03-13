import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Clock, Star, FileText, Activity, BookOpen, ArrowRight } from 'lucide-react'
import * as api from '../api'
import { useAuth } from '../hooks/useAuth'
import { DashboardSkeleton } from '../components/Skeleton'

export default function Dashboard() {
  const { user } = useAuth()

  const { data: recentPages, isLoading: pagesLoading } = useQuery({
    queryKey: ['recentPages'],
    queryFn: api.getRecentPages,
  })

  const { data: activity, isLoading: activityLoading } = useQuery({
    queryKey: ['activity'],
    queryFn: api.getRecentActivity,
  })

  const { data: favoriteSpaces } = useQuery({
    queryKey: ['favoriteSpaces'],
    queryFn: api.getFavoriteSpaces,
  })

  const { data: spaces } = useQuery({
    queryKey: ['spaces'],
    queryFn: api.getSpaces,
  })

  if (pagesLoading && activityLoading) return <DashboardSkeleton />

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Welcome back, {user?.first_name || user?.username}</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Here's what's happening in your wiki</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent pages */}
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <h2 className="font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2"><Clock size={18} /> Recent Pages</h2>
            </div>
            <div className="divide-y divide-gray-100 dark:divide-gray-800">
              {recentPages?.slice(0, 8).map(page => (
                <Link key={page.id} to={`/spaces/${page.space_detail?.key || page.space}/pages/${page.slug}`}
                  className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800">
                  <FileText size={16} className="text-blue-500 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate">{page.title}</p>
                    <p className="text-xs text-gray-400 dark:text-gray-500">{page.space_detail?.name} · {new Date(page.updated_at).toLocaleDateString()}</p>
                  </div>
                </Link>
              ))}
              {(!recentPages || recentPages.length === 0) && (
                <div className="p-8 text-center text-gray-400 dark:text-gray-500">
                  <FileText size={32} className="mx-auto mb-2 opacity-50" />
                  <p>No recent pages</p>
                </div>
              )}
            </div>
          </div>

          {/* Activity feed */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden mt-6">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2"><Activity size={18} /> Recent Activity</h2>
            </div>
            <div className="divide-y divide-gray-100 dark:divide-gray-800">
              {activity?.slice(0, 10).map(a => (
                <div key={a.id} className="flex items-start gap-3 px-4 py-3">
                  <div className="w-7 h-7 rounded-full bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 flex items-center justify-center text-xs font-medium shrink-0 mt-0.5">
                    {a.user?.first_name?.[0] || a.user?.username?.[0] || '?'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      <span className="font-medium">{a.user?.first_name || a.user?.username}</span>{' '}
                      {a.action} <span className="font-medium">{a.target_title}</span>
                    </p>
                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{new Date(a.created_at).toLocaleString()}</p>
                  </div>
                </div>
              ))}
              {(!activity || activity.length === 0) && (
                <div className="p-8 text-center text-gray-400 dark:text-gray-500">
                  <Activity size={32} className="mx-auto mb-2 opacity-50" />
                  <p>No recent activity</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar: Spaces */}
        <div>
          {/* Favorite spaces */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden mb-6">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2"><Star size={18} /> Favorite Spaces</h2>
            </div>
            <div className="divide-y divide-gray-100 dark:divide-gray-800">
              {favoriteSpaces?.map(space => (
                <Link key={space.id} to={`/spaces/${space.key}`}
                  className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800">
                  <div className="w-8 h-8 rounded bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 flex items-center justify-center text-sm font-bold shrink-0">
                    {space.key[0]}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate">{space.name}</p>
                    <p className="text-xs text-gray-400 dark:text-gray-500">{space.key}</p>
                  </div>
                </Link>
              ))}
              {(!favoriteSpaces || favoriteSpaces.length === 0) && (
                <div className="p-6 text-center text-gray-400 dark:text-gray-500 text-sm">No favorite spaces</div>
              )}
            </div>
          </div>

          {/* All spaces */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <h2 className="font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2"><BookOpen size={18} /> All Spaces</h2>
              <Link to="/spaces" className="text-sm text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1">
                View all <ArrowRight size={12} />
              </Link>
            </div>
            <div className="divide-y divide-gray-100 dark:divide-gray-800">
              {spaces?.slice(0, 5).map(space => (
                <Link key={space.id} to={`/spaces/${space.key}`}
                  className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800">
                  <div className="w-8 h-8 rounded bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 flex items-center justify-center text-sm font-bold shrink-0">
                    {space.key[0]}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate">{space.name}</p>
                  </div>
                </Link>
              ))}
              {(!spaces || spaces.length === 0) && (
                <div className="p-6 text-center text-gray-400 dark:text-gray-500 text-sm">
                  <Link to="/spaces/create" className="text-blue-600 dark:text-blue-400 hover:underline">Create your first space</Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

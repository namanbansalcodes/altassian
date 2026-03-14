import { useState, useEffect, useRef } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Search, FileText, BookOpen } from 'lucide-react'
import * as api from '../api'
import { SearchResultsSkeleton } from '../components/Skeleton'
import SEOHead from '../components/SEOHead'

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialQuery = searchParams.get('q') || ''
  const [query, setQuery] = useState(initialQuery)
  const [debouncedQuery, setDebouncedQuery] = useState(initialQuery)
  const inputRef = useRef<HTMLInputElement>(null)

  // Only autofocus on non-touch devices to avoid mobile keyboard pop-up
  useEffect(() => {
    if (window.matchMedia('(pointer: fine)').matches) {
      inputRef.current?.focus()
    }
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query)
      if (query) setSearchParams({ q: query })
    }, 300)
    return () => clearTimeout(timer)
  }, [query])

  const { data: results, isLoading } = useQuery({
    queryKey: ['search', debouncedQuery],
    queryFn: () => api.search(debouncedQuery),
    enabled: debouncedQuery.length > 0,
  })

  return (
    <div className="max-w-3xl mx-auto">
      <SEOHead
        title={debouncedQuery ? `Search: ${debouncedQuery}` : 'Search'}
        description="Search across all Altassian workspaces, pages, and documentation. Find docs, decisions, and knowledge instantly."
        keywords="search, find documents, knowledge base search, wiki search"
        noindex={true}
      />

      <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">Search</h1>

      <div className="relative mb-6">
        <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500" />
        <input
          type="search"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search pages, spaces..."
          ref={inputRef}
          aria-label="Search pages and spaces"
          className="w-full pl-11 pr-4 py-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-xl text-base text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
        />
      </div>

      {isLoading && debouncedQuery && <SearchResultsSkeleton />}

      {results && results.length > 0 && (
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 divide-y divide-gray-100 dark:divide-gray-800 overflow-hidden">
          {results.map(result => (
            <Link key={result.id} to={`/spaces/${result.space?.key}/pages/${result.slug}`}
              className="flex items-start gap-3 px-4 sm:px-5 py-3 sm:py-4 hover:bg-gray-50 dark:hover:bg-gray-800">
              <FileText size={18} className="text-blue-500 shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-semibold text-gray-800 dark:text-gray-200">{result.title}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-2">{result.content_preview}</p>
                <div className="flex items-center gap-2 mt-1.5 text-xs text-gray-400 dark:text-gray-500">
                  <BookOpen size={12} />
                  <span>{result.space?.name}</span>
                  <span>·</span>
                  <span>{new Date(result.updated_at).toLocaleDateString()}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {results && results.length === 0 && debouncedQuery && (
        <div className="text-center py-12">
          <Search size={48} className="mx-auto mb-3 text-gray-300 dark:text-gray-600" />
          <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-1">No results found</h3>
          <p className="text-gray-500 dark:text-gray-400">Try different keywords or check your spelling</p>
        </div>
      )}

      {!debouncedQuery && (
        <div className="text-center py-12">
          <Search size={48} className="mx-auto mb-3 text-gray-300 dark:text-gray-600" />
          <p className="text-gray-500 dark:text-gray-400">Start typing to search across all spaces and pages</p>
        </div>
      )}
    </div>
  )
}

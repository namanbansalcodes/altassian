import { useState, useMemo } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Edit, Clock, Trash2, Paperclip, MessageSquare, Upload, ChevronRight, FileText, Link2 } from 'lucide-react'
import * as api from '../api'
import { toast, getErrorMessage } from '../lib/toast'
import { useAuth } from '../hooks/useAuth'
import { useScrollHint } from '../hooks/useScrollHint'
import { PageViewSkeleton } from '../components/Skeleton'
import SEOHead from '../components/SEOHead'

export default function PageView() {
  const { spaceKey, pageSlug } = useParams<{ spaceKey: string; pageSlug: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user } = useAuth()
  const breadcrumbRef = useScrollHint<HTMLElement>()

  const { data: page, isLoading } = useQuery({
    queryKey: ['page', spaceKey, pageSlug],
    queryFn: () => api.getPage(spaceKey!, pageSlug!),
    enabled: !!spaceKey && !!pageSlug,
  })

  const { data: comments } = useQuery({
    queryKey: ['comments', spaceKey, pageSlug],
    queryFn: () => api.getComments(spaceKey!, pageSlug!),
    enabled: !!spaceKey && !!pageSlug,
  })

  const { data: attachments } = useQuery({
    queryKey: ['attachments', spaceKey, pageSlug],
    queryFn: () => api.getAttachments(spaceKey!, pageSlug!),
    enabled: !!spaceKey && !!pageSlug,
  })

  const deleteMut = useMutation({
    mutationFn: () => api.deletePage(spaceKey!, pageSlug!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pages'] })
      toast.success('Page deleted')
      navigate(`/spaces/${spaceKey}`)
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const [comment, setComment] = useState('')
  const commentMut = useMutation({
    mutationFn: (content: string) => api.createComment(spaceKey!, pageSlug!, { content }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', spaceKey, pageSlug] })
      setComment('')
      toast.success('Comment added')
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const uploadMut = useMutation({
    mutationFn: (file: File) => api.uploadAttachment(spaceKey!, pageSlug!, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['attachments', spaceKey, pageSlug] })
      toast.success('File uploaded')
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const deleteCommentMut = useMutation({
    mutationFn: (id: number) => api.deleteComment(spaceKey!, pageSlug!, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', spaceKey, pageSlug] })
      toast.info('Comment deleted')
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const pageSchema = useMemo(() => {
    if (!page) return undefined
    return {
      '@context': 'https://schema.org',
      '@type': 'Article',
      headline: page.title,
      description: page.meta_description || page.title,
      author: {
        '@type': 'Person',
        name: page.author?.first_name || page.author?.username || 'Unknown',
      },
      datePublished: page.created_at,
      dateModified: page.updated_at,
      publisher: {
        '@type': 'Organization',
        name: 'Altassian',
      },
      mainEntityOfPage: {
        '@type': 'WebPage',
        '@id': `${window.location.origin}/spaces/${spaceKey}/pages/${pageSlug}`,
      },
      breadcrumb: {
        '@type': 'BreadcrumbList',
        itemListElement: [
          {
            '@type': 'ListItem',
            position: 1,
            name: page.space_detail?.name || spaceKey,
            item: `${window.location.origin}/spaces/${spaceKey}`,
          },
          ...(page.parent_detail ? [{
            '@type': 'ListItem',
            position: 2,
            name: page.parent_detail.title,
            item: `${window.location.origin}/spaces/${spaceKey}/pages/${page.parent_detail.slug}`,
          }] : []),
          {
            '@type': 'ListItem',
            position: page.parent_detail ? 3 : 2,
            name: page.title,
          },
        ],
      },
    }
  }, [page, spaceKey, pageSlug])

  if (isLoading) return <PageViewSkeleton />
  if (!page) return <div className="text-center py-12 text-gray-500 dark:text-gray-400">Page not found</div>

  return (
    <div className="max-w-4xl mx-auto">
      <SEOHead
        title={page.title}
        description={page.meta_description || `${page.title} — ${page.space_detail?.name || spaceKey} workspace documentation on Altassian`}
        keywords={page.meta_keywords || ''}
        ogImage={page.og_image || ''}
        ogType="article"
        canonicalUrl={page.canonical_url || `${window.location.origin}/spaces/${spaceKey}/pages/${pageSlug}`}
        noindex={page.noindex || page.is_draft}
        schema={pageSchema}
      />

      {/* Breadcrumbs */}
      <nav ref={breadcrumbRef} className="breadcrumb-scroll flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400 mb-4 pb-1" aria-label="Breadcrumb">
        <Link to={`/spaces/${spaceKey}`} className="hover:text-blue-600 dark:hover:text-blue-400 shrink-0">{page.space_detail?.name || spaceKey}</Link>
        {page.parent_detail && (
          <>
            <ChevronRight size={14} className="shrink-0" aria-hidden="true" />
            <Link to={`/spaces/${spaceKey}/pages/${page.parent_detail.slug}`} className="hover:text-blue-600 dark:hover:text-blue-400 shrink-0">{page.parent_detail.title}</Link>
          </>
        )}
        <ChevronRight size={14} className="shrink-0" aria-hidden="true" />
        <span className="text-gray-800 dark:text-gray-200 truncate">{page.title}</span>
      </nav>

      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between mb-6 gap-3">
        <div className="min-w-0">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-gray-100 break-words">{page.title}</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            By {page.author?.first_name || page.author?.username} · Updated {new Date(page.updated_at).toLocaleDateString()}
          </p>
        </div>
        <div className="flex items-center gap-1.5 sm:gap-2 shrink-0 flex-wrap sm:flex-nowrap">
          <Link to={`/spaces/${spaceKey}/pages/${pageSlug}/edit`}
            className="flex items-center gap-1.5 px-3 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
            <Edit size={14} /> Edit
          </Link>
          <Link to={`/spaces/${spaceKey}/pages/${pageSlug}/history`}
            className="flex items-center gap-1.5 px-3 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg text-sm hover:bg-gray-50 dark:hover:bg-gray-800">
            <Clock size={14} /> <span className="hidden sm:inline">History</span>
          </Link>
          <button onClick={() => {
            navigator.clipboard.writeText(window.location.href)
              .then(() => toast.success('Link copied'))
              .catch(() => toast.error('Failed to copy link'))
          }}
            className="flex items-center justify-center px-3 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg text-sm hover:bg-gray-50 dark:hover:bg-gray-800"
            title="Copy page link">
            <Link2 size={14} />
          </button>
          <button onClick={() => { if (confirm('Delete this page?')) deleteMut.mutate() }}
            className="flex items-center justify-center px-3 py-2 border border-red-300 dark:border-red-700 text-red-600 dark:text-red-400 rounded-lg text-sm hover:bg-red-50 dark:hover:bg-red-900/20">
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {/* Content */}
      <article className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-4 sm:p-6 md:p-8 mb-8 prose prose-blue dark:prose-invert max-w-none prose-responsive"
        dangerouslySetInnerHTML={{ __html: page.content || '<p class="text-gray-400">No content yet</p>' }} />

      {/* Attachments */}
      <section className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-4 sm:p-6 mb-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base sm:text-lg font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2"><Paperclip size={18} /> Attachments</h3>
          <label className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg text-sm hover:bg-gray-200 dark:hover:bg-gray-700 cursor-pointer">
            <Upload size={14} /> Upload
            <input type="file" className="hidden" onChange={e => { if (e.target.files?.[0]) uploadMut.mutate(e.target.files[0]) }} />
          </label>
        </div>
        {attachments?.length ? (
          <ul className="divide-y divide-gray-100 dark:divide-gray-800">
            {attachments.map(att => (
              <li key={att.id} className="attachment-row flex items-center gap-2 py-2.5 min-w-0 flex-wrap sm:flex-nowrap">
                <FileText size={14} className="text-gray-400 shrink-0" />
                <a href={att.file} target="_blank" rel="noreferrer" className="text-sm text-blue-600 dark:text-blue-400 hover:underline truncate flex-1 min-w-0 break-all">{att.filename}</a>
                <span className="text-xs text-gray-400 dark:text-gray-500 shrink-0">{(((att.file_size ?? 0) / 1024).toFixed(1))} KB</span>
              </li>
            ))}
          </ul>
        ) : <p className="text-sm text-gray-400 dark:text-gray-500">No attachments</p>}
      </section>

      {/* Comments */}
      <section className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-4 sm:p-6">
        <h3 className="text-base sm:text-lg font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2 mb-4"><MessageSquare size={18} /> Comments</h3>
        <div className="space-y-4 mb-6">
          {comments?.map(c => (
            <div key={c.id} className="flex gap-2 sm:gap-3">
              <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 flex items-center justify-center text-xs sm:text-sm font-medium shrink-0">
                {c.author?.first_name?.[0] || c.author?.username?.[0] || '?'}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
                  <span className="text-sm font-medium text-gray-800 dark:text-gray-200">{c.author?.first_name || c.author?.username}</span>
                  <span className="text-xs text-gray-400 dark:text-gray-500">{new Date(c.created_at).toLocaleDateString()}</span>
                  {c.author?.id === user?.id && (
                    <button data-compact-touch onClick={() => deleteCommentMut.mutate(c.id)} className="text-xs text-red-400 hover:text-red-600 dark:hover:text-red-300 px-1.5 py-0.5 rounded">Delete</button>
                  )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 break-words">{c.content}</p>
              </div>
            </div>
          ))}
          {(!comments || comments.length === 0) && <p className="text-sm text-gray-400 dark:text-gray-500">No comments yet</p>}
        </div>
        <form onSubmit={e => { e.preventDefault(); if (comment.trim()) commentMut.mutate(comment.trim()) }} className="flex flex-col sm:flex-row gap-2 sm:gap-3">
          <input value={comment} onChange={e => setComment(e.target.value)} placeholder="Add a comment..."
            className="flex-1 px-3 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg text-base sm:text-sm text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 outline-none" />
          <button type="submit" disabled={!comment.trim() || commentMut.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 shrink-0">
            Comment
          </button>
        </form>
      </section>
    </div>
  )
}

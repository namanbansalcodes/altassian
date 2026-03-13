import api, { setAccessToken } from './client'
import type {
  AuthTokens, LoginCredentials, RegisterData,
  Space, Page, PageVersion, Comment, Attachment, SearchResult, Activity, User
} from '../types'

// Helpers
async function resolvePageId(spaceKey: string, pageSlug: string): Promise<number> {
  const { data } = await api.get('/pages/by-slug/', { params: { space_key: spaceKey, slug: pageSlug } })
  return data.id
}

// Auth
export async function login(creds: LoginCredentials): Promise<AuthTokens> {
  const { data } = await api.post<AuthTokens>('/auth/login/', creds)
  setAccessToken(data.access)
  localStorage.setItem('refresh_token', data.refresh)
  return data
}

export async function refreshFromStorage(): Promise<string | null> {
  const refresh = localStorage.getItem('refresh_token')
  if (!refresh) return null
  try {
    const { data } = await api.post<AuthTokens>('/auth/token/refresh/', { refresh })
    setAccessToken(data.access)
    return data.access
  } catch {
    localStorage.removeItem('refresh_token')
    setAccessToken(null)
    return null
  }
}

export async function register(data: RegisterData): Promise<User> {
  const { data: user } = await api.post<User>('/users/register/', data)
  return user
}

export async function logout() {
  localStorage.removeItem('refresh_token')
  setAccessToken(null)
}

export async function getMe(): Promise<User> {
  const { data } = await api.get<User>('/users/me/')
  return data
}

// Spaces
export async function getSpaces(): Promise<Space[]> {
  const { data } = await api.get('/spaces/')
  return (data.results || data) as any
}

export async function getSpace(key: string): Promise<Space> {
  const { data } = await api.get(`/spaces/${key}/`)
  return data as any
}

export async function createSpace(space: Partial<Space>): Promise<Space> {
  const { data } = await api.post('/spaces/', space)
  return data as any
}

export async function updateSpace(key: string, space: Partial<Space>): Promise<Space> {
  const { data } = await api.patch(`/spaces/${key}/`, space)
  return data as any
}

export async function deleteSpace(key: string): Promise<void> {
  await api.delete(`/spaces/${key}/`)
}

// Pages
export async function getPages(spaceKey: string): Promise<any[]> {
  const { data } = await api.get('/pages/tree/', { params: { space_key: spaceKey } })
  return data as any[]
}

export async function getPage(spaceKey: string, pageSlug: string): Promise<any> {
  const { data } = await api.get('/pages/by-slug/', { params: { space_key: spaceKey, slug: pageSlug } })
  // Map backend to frontend expectations
  return {
    id: data.id,
    title: data.title,
    slug: data.slug,
    content: data.body_html,
    space: data.space,
    parent: data.parent,
    created_at: data.created_at,
    updated_at: data.updated_at,
    author: { id: data.created_by, username: data.created_by_username },
  }
}

export async function createPage(spaceKey: string, page: Partial<Page>): Promise<any> {
  // Expecting page to carry title/body_markdown/body_html/parent/position
  // Need space id; fetch space detail to get id
  const { data: space } = await api.get(`/spaces/${spaceKey}/`)
  const payload: any = { ...page, space: space.id }
  const { data } = await api.post('/pages/', payload)
  return data
}

export async function updatePage(spaceKey: string, pageSlug: string, page: Partial<Page>): Promise<any> {
  const id = await resolvePageId(spaceKey, pageSlug)
  const { data } = await api.patch(`/pages/${id}/`, page)
  return data
}

export async function deletePage(spaceKey: string, pageSlug: string): Promise<void> {
  const id = await resolvePageId(spaceKey, pageSlug)
  await api.delete(`/pages/${id}/`)
}

// Page versions
export async function getPageVersions(spaceKey: string, pageSlug: string): Promise<PageVersion[]> {
  const id = await resolvePageId(spaceKey, pageSlug)
  const { data } = await api.get('/page-versions/', { params: { page: id } })
  return data.results || data
}

export async function getPageVersion(_spaceKey: string, _pageSlug: string, versionId: number): Promise<PageVersion> {
  const { data } = await api.get<PageVersion>(`/page-versions/${versionId}/`)
  return data
}

// Comments
export async function getComments(spaceKey: string, pageSlug: string): Promise<Comment[]> {
  const id = await resolvePageId(spaceKey, pageSlug)
  const { data } = await api.get('/comments/', { params: { page: id, ordering: 'created_at' } })
  const list = data.results || data
  return list.map((c: any) => ({
    id: c.id,
    page: c.page,
    author: { id: c.author, username: c.author_username },
    content: c.body,
    parent: c.parent,
    created_at: c.created_at,
  }))
}

export async function createComment(spaceKey: string, pageSlug: string, comment: Partial<Comment>): Promise<Comment> {
  const id = await resolvePageId(spaceKey, pageSlug)
  const { data } = await api.post('/comments/', { page: id, body: comment.content || comment.body })
  return data
}

export async function deleteComment(_spaceKey: string, _pageSlug: string, commentId: number): Promise<void> {
  await api.delete(`/comments/${commentId}/`)
}

// Attachments
export async function getAttachments(spaceKey: string, pageSlug: string): Promise<Attachment[]> {
  const id = await resolvePageId(spaceKey, pageSlug)
  const { data } = await api.get('/attachments/', { params: { page: id } })
  return (data.results || data).map((a: any) => ({
    id: a.id,
    page: a.page,
    file: a.file,
    filename: a.file.split('/').pop(),
    file_size: a.file_size || 0,
    content_type: a.content_type || '',
    uploaded_by: { id: a.uploaded_by, username: a.uploaded_by_username },
    created_at: a.created_at,
  }))
}

export async function uploadAttachment(spaceKey: string, pageSlug: string, file: File): Promise<Attachment> {
  const id = await resolvePageId(spaceKey, pageSlug)
  const formData = new FormData()
  formData.append('page', String(id))
  formData.append('file', file)
  const { data } = await api.post(
    '/attachments/',
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
  return data
}

export async function deleteAttachment(_spaceKey: string, _pageSlug: string, attachmentId: number): Promise<void> {
  await api.delete(`/attachments/${attachmentId}/`)
}

// Search
export async function search(query: string): Promise<SearchResult[]> {
  const { data } = await api.get('/pages/search/', { params: { q: query } })
  const list = data.results || []
  return list.map((p: any) => ({
    id: p.id,
    title: p.title,
    content_preview: p.body_markdown?.slice(0, 140) || '',
    space: p.space,
    page_type: p.is_draft ? 'draft' : 'page',
    updated_at: p.updated_at,
    slug: p.slug,
  }))
}

// Activity / Dashboard
export async function getRecentActivity(): Promise<Activity[]> {
  const { data } = await api.get('/pages/activity/')
  const list = data.results || []
  return list.map((p: any) => ({
    id: p.id,
    user: { id: p.updated_by, username: p.updated_by_username },
    action: 'updated',
    target_type: 'page',
    target_title: p.title,
    created_at: p.updated_at,
    space: p.space,
  }))
}

export async function getRecentPages(): Promise<any[]> {
  const { data } = await api.get('/pages/', { params: { ordering: '-updated_at' } })
  return (data.results || data) as any[]
}

export async function getFavoriteSpaces(): Promise<Space[]> {
  // Not implemented; return first few spaces as pseudo-favorites
  const spaces = await getSpaces()
  return spaces.slice(0, 3)
}

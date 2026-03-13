export interface User {
  id: number
  username: string
  email?: string
  first_name?: string
  last_name?: string
}

export interface Space {
  id: number
  key: string
  name: string
  description?: string
  // Normalize to a full User object when present; null when unknown
  owner?: User | null
  created_at?: string
  updated_at?: string
}

export interface Page {
  id: number
  title: string
  slug: string
  content?: string
  space: number
  space_detail?: Space
  parent?: number | null
  parent_detail?: Page
  author?: User
  children?: Page[]
  depth?: number
  position?: number
  is_published?: boolean
  created_at?: string
  updated_at?: string
}

export interface PageVersion {
  id: number
  page: number
  title?: string
  content?: string
  version_number: number
  author?: User
  change_message?: string
  created_at: string
}

export interface Comment {
  id: number
  page: number
  author?: User
  content?: string
  body?: string
  parent?: number | null
  replies?: Comment[]
  created_at: string
  updated_at?: string
}

export interface Attachment {
  id: number
  page: number
  file: string
  filename?: string
  file_size?: number
  content_type?: string
  uploaded_by?: User
  created_at: string
}

export interface SearchResult {
  id: number
  title: string
  content_preview: string
  space: any
  page_type: string
  updated_at: string
  slug: string
}

export interface Activity {
  id: number
  user: User
  action: string
  target_type: string
  target_title: string
  space?: any
  created_at: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  password_confirm: string
  first_name: string
  last_name: string
}

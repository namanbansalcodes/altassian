export type Role = "admin" | "member";

export interface User {
  id: number;
  email: string;
  display_name: string;
  avatar_url: string;
  role: Role;
  joined_at: string;
}

export interface Space {
  id: number;
  slug: string;
  name: string;
  description: string;
  icon: string;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface PageNode {
  id: number;
  slug: string;
  title: string;
  is_draft: boolean;
  is_public: boolean;
  position: number;
  children: PageNode[];
}

export interface SpaceDetail extends Space {
  pages: PageNode[];
}

export interface PageDetail {
  id: number;
  space: number;
  parent: number | null;
  slug: string;
  title: string;
  body_md: string;
  body_html: string;
  position: number;
  is_public: boolean;
  is_draft: boolean;
  created_by: number;
  updated_by: number;
  created_at: string;
  updated_at: string;
}

export interface SearchResult {
  page_id: number;
  space_slug: string;
  page_slug: string;
  title: string;
  snippet_html: string;
  rank: number;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

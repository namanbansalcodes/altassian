You are building the frontend for Altassian, a Confluence/wiki clone. The backend API is at http://localhost:8000/api/.

Create a full React + TypeScript app with Vite:
1. npm create vite@latest . -- --template react-ts (if package.json missing)
2. Install: axios, react-router-dom, @tanstack/react-query, @tiptap/react, @tiptap/starter-kit, @tiptap/extension-placeholder, tailwindcss, @headlessui/react, lucide-react
3. Project structure: src/{components,pages,hooks,api,store,types}
4. API client with axios interceptors for JWT (access token in memory, refresh token in httpOnly cookie or localStorage)
5. Auth pages: Login, Register with form validation
6. Layout: Sidebar with space list + collapsible page tree, main content area, top navbar with search + user menu
7. Space pages: List all spaces, Create space, Space settings
8. Page viewer: Render HTML content, show breadcrumbs, comments section, attachment list
9. Page editor: TipTap rich text editor with toolbar (bold, italic, headings, lists, code blocks, links, images)
10. Page history: Version list with diff viewer
11. Search page: Live search results across all spaces and pages
12. Dashboard: Recent activity feed, favorite spaces, recent pages
13. Make it look polished — use Tailwind for a clean Confluence-like UI with a blue/white theme
14. Git init and commit

When completely finished, run: openclaw system event --text "Done: Altassian frontend complete — auth, spaces, pages, editor, search, versioning UI all working" --mode now

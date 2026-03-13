# Altassian Frontend

A Confluence-like wiki editor built with React, TypeScript, and TipTap.

## Editor Features

### Floating Toolbar (Bubble Menu)
Select any text to reveal a floating toolbar with:
- **Text formatting**: Bold (`Ctrl+B`), Italic (`Ctrl+I`), Underline (`Ctrl+U`), Strikethrough (`Ctrl+Shift+S`), Inline Code (`Ctrl+E`)
- **Links**: Add/edit/remove links (`Ctrl+K`)
- **Headings**: H1, H2, H3 toggle
- **Lists**: Bullet list, Ordered list
- **Blocks**: Blockquote, Code block
- **Alignment**: Left, Center, Right
- **Clear formatting**: Remove all marks and reset to paragraph

**Keyboard navigation within toolbar:**
- `Arrow Left / Right` — move focus between toolbar buttons
- `Arrow Up / Down` — also navigates buttons
- `Enter / Space` — activate focused button
- `Escape` — dismiss toolbar and return focus to editor

### Slash Commands
Type `/` at the start of a line or after whitespace to open the command palette:
- **Heading 1/2/3** — section headings
- **Paragraph** — plain text
- **Bullet List / Ordered List / Task List** — list types
- **Quote** — blockquote
- **Code Block** — fenced code
- **Divider** — horizontal rule
- **Image** — opens file picker
- **Table** — inserts a 3×3 table
- **Page Link** — link to another page (prompts for URL/slug)
- **Callout** — info block (blockquote variant)
- **Mention** — @mention stub

Navigate with `↑`/`↓` arrows, select with `Enter`, dismiss with `Escape`. Supports fuzzy filtering as you type. Menu auto-repositions to stay within the viewport.

### Keyboard Shortcuts
| Action | Shortcut |
|--------|----------|
| Bold | `Ctrl+B` |
| Italic | `Ctrl+I` |
| Underline | `Ctrl+U` |
| Strikethrough | `Ctrl+Shift+S` |
| Code | `Ctrl+E` |
| Link | `Ctrl+K` |
| Undo | `Ctrl+Z` |
| Redo | `Ctrl+Shift+Z` |

### Manual Test Plan

#### Floating Toolbar
1. Open the page editor (`/spaces/:key/pages/new` or edit an existing page).
2. Type some text and select a portion of it.
3. Verify the floating toolbar appears above the selection.
4. Click **Bold** — verify text becomes bold and button highlights.
5. Click **Strikethrough** — verify strikethrough is applied.
6. Click **Add Link** — verify the URL input form appears; enter a URL and click Apply.
7. Click **Clear Formatting** — verify all formatting is removed.
8. Use `Tab` to focus the toolbar, then `Arrow Right/Left` to move between buttons.
9. Press `Escape` — verify toolbar closes and editor regains focus.
10. Toggle dark mode — verify toolbar remains readable.
11. Select text inside a code block — verify toolbar does **not** appear.

#### Slash Commands
1. In the editor, press `/` at the start of a new line.
2. Verify the command palette appears below the cursor.
3. Type `head` — verify the list filters to Heading 1/2/3.
4. Press `Arrow Down` twice, then `Enter` — verify the selected heading is inserted.
5. Type `/todo` — verify Task List appears; press Enter to insert.
6. Type `/page` — verify Page Link appears; press Enter; enter a URL in the prompt.
7. Press `Escape` — verify menu dismisses without inserting anything.
8. Scroll down so the cursor is near viewport bottom, type `/` — verify menu repositions to stay visible.
9. Toggle dark mode — verify menu colors adapt.

#### Persistence
1. Create a page with various formatting (headings, lists, links, code blocks).
2. Save the page.
3. Re-open the page — verify all content and formatting is preserved.

## Dark Mode / Theming

Altassian supports light and dark themes with a toggle in the top navigation bar.

### How it works

1. **Class-based dark mode**: A `.dark` class on `<html>` activates Tailwind's `dark:` variant via `@custom-variant dark` in `index.css`. A `data-theme="light|dark"` attribute is also set for CSS variable scoping.
2. **CSS variable tokens**: Semantic color tokens (e.g. `--color-background`, `--color-text-primary`, `--color-accent`) are defined on `:root` and `:root.dark` in `index.css`. These can be used directly in custom CSS or inline styles.
3. **System preference**: On first visit (no stored preference), the app matches the OS `prefers-color-scheme` setting.
4. **Persistence**: The user's choice is saved to `localStorage` under `altassian-theme` and restored on subsequent visits.
5. **No flash (FOUC prevention)**: An inline `<script>` in `index.html` reads localStorage/system preference and sets both `.dark` class and `data-theme` attribute before any rendering.
6. **Smooth transitions**: Background, border, and text colors transition over 200ms. Users who prefer reduced motion see instant changes.
7. **TipTap editor**: The editor uses `dark:prose-invert` plus custom dark styles in `index.css` for code blocks, tables, blockquotes, links, and selections.

### Toggle location

The sun/moon icon button is in the header, between the search bar and the user profile menu. It has an `aria-label` for accessibility.

### Key files

| File | Role |
|------|------|
| `src/hooks/useTheme.ts` | Theme context, toggle logic, localStorage + system preference |
| `src/index.css` | `@custom-variant dark`, transition rules, TipTap dark styles |
| `index.html` | Inline no-flash script |
| `src/components/Layout.tsx` | Toggle button in header |
| `src/App.tsx` | `ThemeContext.Provider` wrapping the app |

### Available CSS variable tokens

All tokens are defined in `src/index.css` under `:root` (light) and `:root.dark` (dark):

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--color-background` | `#ffffff` | `#030712` | Page background |
| `--color-surface` | `#f9fafb` | `#111827` | Card/section backgrounds |
| `--color-surface-raised` | `#ffffff` | `#1f2937` | Elevated surfaces (modals, dropdowns) |
| `--color-text-primary` | `#111827` | `#f3f4f6` | Main text |
| `--color-text-secondary` | `#6b7280` | `#9ca3af` | Secondary/label text |
| `--color-text-muted` | `#9ca3af` | `#6b7280` | Placeholder/hint text |
| `--color-border` | `#e5e7eb` | `#374151` | Borders |
| `--color-border-subtle` | `#f3f4f6` | `#1f2937` | Subtle dividers |
| `--color-accent` | `#2563eb` | `#3b82f6` | Primary action color |
| `--color-accent-hover` | `#1d4ed8` | `#60a5fa` | Hovered accent |
| `--color-accent-subtle` | `#eff6ff` | `rgba(59,130,246,0.15)` | Accent backgrounds |
| `--color-success` | `#16a34a` | `#22c55e` | Success states |
| `--color-warning` | `#d97706` | `#f59e0b` | Warning states |
| `--color-error` | `#dc2626` | `#ef4444` | Error states |
| `--color-code-bg` | `#f1f5f9` | `#334155` | Inline code background |
| `--color-code-text` | `#e11d48` | `#fb7185` | Inline code text |
| `--color-editor-bg` | `#ffffff` | `#111827` | Editor content area |
| `--color-editor-toolbar` | `#f9fafb` | `#1f2937` | Editor toolbar |

### Adding new tokens

1. Add the CSS variable to both `:root` and `:root.dark` in `src/index.css`.
2. Use the token in CSS: `background: var(--color-surface);` or in Tailwind: `bg-[var(--color-surface)]`.

### Extending the theme

To add dark mode support to a new component:

1. Use Tailwind's `dark:` prefix on color utilities: `bg-white dark:bg-gray-900`, `text-gray-800 dark:text-gray-200`, etc.
2. For custom CSS, use the `:where(.dark)` selector or CSS variable tokens (see `index.css` for examples).
3. Access the current theme programmatically via `useTheme()` from `src/hooks/useTheme.ts`:
   ```tsx
   import { useTheme } from '../hooks/useTheme'
   const { theme, toggleTheme } = useTheme()
   ```
4. Color palette guidelines:
   - **Backgrounds**: `gray-50`/`gray-950` (page), `white`/`gray-900` (cards), `gray-100`/`gray-800` (inputs)
   - **Text**: `gray-900`/`gray-100` (primary), `gray-500`/`gray-400` (secondary)
   - **Borders**: `gray-200`/`gray-700`
   - **Accent badges**: `blue-100`/`blue-900/40` bg, `blue-700`/`blue-400` text

## Toast Notifications

A lightweight, type-safe toast system built on [sonner](https://sonner.emilkowal.dev/). Toasts are accessible, respect light/dark themes, honor `prefers-reduced-motion`, and queue up to 3 visible at a time.

### Quick Start

```tsx
import { toast } from '../lib/toast'

// Direct helpers
toast.success('Page saved')
toast.error('Something went wrong')
toast.info('Autosaved', { duration: 1500 })
toast.warning('Unsaved changes')

// Variant-driven
toast.show({ title: 'Saved', description: 'Your page is live', variant: 'success' })
```

### useToast() Hook

```tsx
import { useToast } from '../hooks/useToast'

function MyComponent() {
  const { toast, toastSuccess, toastError } = useToast()

  const handleSave = async () => {
    try {
      await savePage()
      toastSuccess('Page saved')
    } catch (err) {
      toastError(getErrorMessage(err))
    }
  }

  // Or use the variant-driven API:
  toast({ title: 'Done', variant: 'success', description: 'All changes saved' })
}
```

### Convenience Imports

```tsx
import { toastSuccess, toastError, toastInfo, toastWarning } from '../lib/toast'

toastSuccess('Created!')
toastError('Failed to delete')
```

### Wired Events

| Event | Variant | Location |
|-------|---------|----------|
| Login success | `success` | LoginPage |
| Login failure | `error` | LoginPage |
| Register success | `success` | RegisterPage |
| Logout | `success` | Layout |
| Page save/create | `success` | PageEditor |
| Page save error | `error` | PageEditor |
| Autosave (30s debounce) | `info` | PageEditor |
| Copy page link | `success` | PageView |
| Comment/attachment CRUD | `success`/`error` | PageView |
| Theme toggle | `info` (1.5s) | Layout |
| Network error | `error` | Axios interceptor |
| Server 5xx | `error` | Axios interceptor |

### Configuration

The `<Toaster>` component is mounted in `main.tsx` with:
- **Position**: bottom-right
- **Max visible**: 3 toasts
- **Duration**: 3.5s default
- **Theme**: system (follows light/dark)
- **Close button**: visible
- **Rich colors**: enabled

## Running Tests
```bash
npm test          # single run
npm run test:watch # watch mode
```

## Loading Skeletons

Reusable skeleton/placeholder components that show shimmer placeholders while data loads, replacing generic spinners with layout-aware previews.

### Key files

| File | Role |
|------|------|
| `src/components/Skeleton.tsx` | All skeleton primitives and page-level compositions |
| `src/components/RouteLoadingBar.tsx` | Thin progress bar shown during route transitions |
| `src/index.css` | `skeleton-shimmer` keyframes and dark-mode / reduced-motion support |
| `src/components/__tests__/Skeleton.test.tsx` | Unit tests for every skeleton variant |

### Base primitives

All primitives accept a `size` prop (`'sm' | 'md' | 'lg'`) that maps to sensible defaults:

| Component | Props | Description |
|-----------|-------|-------------|
| `<Skeleton>` | `width`, `height`, `rounded`, `className` | Base shimmer block |
| `<SkeletonLine>` | `width`, `height`, `size` | Single text-like line (sm=10px, md=14px, lg=20px) |
| `<SkeletonCircle>` | `size`, `diameter` | Circular avatar placeholder (sm=24px, md=32px, lg=48px) |
| `<SkeletonTitle>` | `width`, `size` | Heading placeholder (sm=16px, md=24px, lg=32px) |
| `<SkeletonIcon>` | `size` | Small square icon placeholder (sm=14px, md=20px, lg=28px) |

### Compositions

| Component | Use case |
|-----------|----------|
| `<SkeletonText lines={n} size>` | Paragraph placeholder |
| `<SkeletonListItem>` | Avatar + two-line row |
| `<SkeletonTreeItem indent={n}>` | Sidebar tree node |
| `<SkeletonToolbar>` | Editor formatting toolbar |
| `<SkeletonCard>` | Space card in grid |

### Page-level skeletons

| Component | Used in |
|-----------|---------|
| `<AppChromeSkeleton>` | `App.tsx` — full app shell (topbar + sidebar + content) during auth check |
| `<SidebarSkeleton>` | `Sidebar.tsx` — while spaces load |
| `<DashboardSkeleton>` | `Dashboard.tsx` — initial mount |
| `<SpaceListSkeleton>` | `SpaceList.tsx` — space grid with header |
| `<PageViewSkeleton>` | `PageView.tsx` — page detail loading |
| `<EditorSkeleton>` | `PageEditor.tsx` — editing existing page |
| `<SpaceViewSkeleton>` | `SpaceView.tsx` — space page list |
| `<HistorySkeleton>` | `PageHistory.tsx` — version list |
| `<SearchResultsSkeleton>` | `SearchPage.tsx` — while searching |
| `<SettingsSkeleton>` | `SpaceSettings.tsx` — settings form |

### Route transition loading bar

`<RouteLoadingBar />` is mounted in `Layout.tsx` and uses React Router's `useNavigation()` to show a thin blue progress bar at the top of the viewport during client-side navigations. It auto-hides after the navigation completes.

### Usage

```tsx
import { PageViewSkeleton } from '../components/Skeleton'

const { data, isLoading } = useQuery({ ... })
if (isLoading) return <PageViewSkeleton />
```

### Adding a new skeleton for a page

1. Create a new exported function in `src/components/Skeleton.tsx`:
   ```tsx
   export function MyPageSkeleton() {
     return (
       <div className="max-w-4xl mx-auto" role="status" aria-label="Loading my page">
         <SkeletonTitle width={200} size="lg" />
         <SkeletonText lines={4} />
       </div>
     )
   }
   ```
2. Use the size-aware primitives (`SkeletonLine`, `SkeletonTitle`, `SkeletonIcon`, `SkeletonCircle`) with `size="sm" | "md" | "lg"` instead of hardcoding pixel heights.
3. Always add `role="status"` and a descriptive `aria-label` on the outer wrapper.
4. Wire it to the page's loading state:
   ```tsx
   if (isLoading) return <MyPageSkeleton />
   ```
5. Add a test case to `src/components/__tests__/Skeleton.test.tsx` in the `pageLevelSkeletons` array.

### Design notes

- **Shimmer animation** uses CSS `background-position` animation (1.8s ease-in-out loop).
- **Reduced motion**: Animation is disabled via `@media (prefers-reduced-motion: reduce)`.
- **Dark mode**: Skeleton colors use CSS custom properties (`--skeleton-base`, `--skeleton-shine`) that swap under `.dark`.
- **Accessibility**: All page-level skeletons carry `role="status"` with descriptive `aria-label`.
- All skeletons are wired to real React Query `isLoading` states — no fake timeouts.
- **Route transitions**: A `<RouteLoadingBar />` in `Layout.tsx` provides visual feedback during page navigations.

---

## Sidebar Tree

The left sidebar displays a collapsible, hierarchical page tree under each space.

### Features

- **Expand/Collapse**: Click the chevron to expand or collapse a space or parent page.
- **Indentation by depth**: Nested pages are visually indented to show hierarchy.
- **Active highlight**: The current space and page are highlighted based on the URL.
- **Lazy loading**: Pages for a space are fetched only when the space is expanded and cached with React Query.
- **Persistent state**: Expanded space keys and page ids are saved per-space in `localStorage` (`altassian:sidebar:<spaceKey>`), so tree state survives reloads.
- **Auto-expand ancestors**: When navigating directly to a nested page, its parent chain expands automatically.
- **Auto-scroll into view**: The active page node is smoothly scrolled into the visible sidebar area on route change.
- **Empty state**: Spaces with no pages show an illustration and a "Create first page" CTA linking to the editor.
- **Drag-and-drop**: Pages can be dragged to reorder within a space (UI-only — server call is guarded behind feature flag until backend endpoint is available).
- **Add page shortcut**: Each expanded space shows an "Add page" link.

### Keyboard Shortcuts

When a space tree has focus:

| Key | Action |
|-----|--------|
| `↑` / `↓` | Move selection up/down within visible nodes |
| `→` | Expand the focused node (or expand space if collapsed) |
| `←` | Collapse the focused node (or collapse space) |
| `Enter` | Navigate to the focused page |
| `Home` | Jump to space header |
| `End` | Jump to last visible node |

### Accessibility

- Container uses `role="tree"`, items use `role="treeitem"`.
- `aria-expanded` on spaces and parent pages.
- `aria-selected` on the active page.
- `aria-level` indicates nesting depth.
- Roving `tabIndex` for keyboard navigation.

### Key Files

| File | Role |
|------|------|
| `src/components/Sidebar.tsx` | Main sidebar component with tree rendering |
| `src/hooks/useSidebarTree.ts` | Hooks for expanded state management and page fetching |
| `src/lib/tree.ts` | Tree flattening, ancestor lookup, localStorage helpers |
| `src/components/__tests__/Sidebar.test.tsx` | Unit and component tests |

### How Expanded State Persistence Works

Expanded state is stored in `localStorage` under the prefix `altassian:sidebar:`:
- **Space expansion**: `altassian:sidebar:spaces` — JSON array of expanded space keys.
- **Page expansion**: `altassian:sidebar:<spaceKey>` — JSON array of expanded page IDs, scoped per space.

On mount, `useExpandedSpaces()` and `useSpaceTree()` load from localStorage. Every toggle writes back immediately. Corrupt data is handled gracefully (falls back to empty set).

### Extending the Tree

To add new node types or behaviors:
1. **New node metadata**: Extend the `FlatTreeNode` interface in `src/lib/tree.ts` and update `flattenTree()`.
2. **Custom rendering**: Modify `PageTreeRow` in `Sidebar.tsx` or create a new row component for the new node type.
3. **Additional actions**: Add context menu items or buttons inside `PageTreeRow` — use `e.stopPropagation()` to prevent row click navigation.
4. **Server-side reorder**: When the backend supports page reorder, update the `handleDrop` callback in `PageTreeRow` to call the API and invalidate the `['pages', spaceKey]` query cache.

---

## Responsive Layout

The UI is fully responsive across mobile (< 640px), tablet (640–1024px), and desktop (1024px+) viewports. The app is usable end-to-end on a 375px screen without horizontal scrolling.

### Breakpoints (Tailwind v4 defaults)

| Token | Width | Usage |
|-------|-------|-------|
| `sm` | 640px | Stack → side-by-side transitions, tighter padding |
| `md` | 768px | Header nav links appear, grid columns increase |
| `lg` | 1024px | Sidebar becomes persistent; full desktop layout |
| `xl` | 1280px | Max-width containers widen |

### Breakpoint behavior

| Viewport | Sidebar | Header nav links | Content padding |
|----------|---------|------------------|-----------------|
| **< lg (1024px)** | Off-canvas drawer (hamburger toggle) | Inside drawer (< md) or header (md+) | Compact (`p-3`/`p-4`) |
| **lg+** | Persistent, fixed-width, collapsible | Always visible in header | Full (`p-6`) |

### Key components

| Component | File | Description |
|-----------|------|-------------|
| `Layout` | `src/components/Layout.tsx` | Shell with responsive header, mobile drawer, desktop sidebar, main outlet |
| `Sidebar` | `src/components/Sidebar.tsx` | Page tree — rendered inside drawer on mobile, inline on desktop |
| `ResponsiveTable` | `src/components/ResponsiveTable.tsx` | Wrapper that adds horizontal scroll for wide tables on small screens |

### Mobile sidebar drawer

- Built with Headless UI `Dialog` + `Transition` for accessibility (focus trap, Esc to close, overlay click to close).
- Slides in from the left with CSS transitions.
- Auto-closes when the viewport grows past `lg` (1024px).
- Includes mobile nav links (Home, Spaces, Create) when the header nav is hidden.
- ARIA labels on hamburger and close buttons.

### Editor responsiveness

- The static toolbar in `PageEditor` scrolls horizontally on small screens (`overflow-x-auto`) and wraps on larger screens.
- The TipTap editor content area uses responsive padding and `prose-responsive` for word-break and image scaling.
- Tables inside the editor have `min-width` and scroll horizontally via `.tiptap-table-wrap` / `.prose-responsive table`.
- Title input uses responsive font size (`text-xl sm:text-2xl`) and padding.

### Page-level responsive patterns

| Page | Pattern |
|------|---------|
| **Login/Register** | Centered card with `px-4` safe area; form padding scales `p-5 sm:p-8`; name fields stack on mobile (`grid-cols-1 sm:grid-cols-2`); buttons ≥44px tap target |
| **Landing** | Hero text scales `text-3xl sm:text-4xl md:text-6xl`; features grid `grid-cols-1 sm:grid-cols-2 md:grid-cols-3`; footer stacks on mobile |
| **Dashboard** | `grid-cols-1 lg:grid-cols-3` for main/sidebar layout |
| **PageView** | Sections use `p-4 sm:p-6`; action buttons flex-wrap; attachment filenames truncate |
| **PageEditor** | Toolbar `overflow-x-auto` on mobile, wraps on desktop; title `px-4 sm:px-6` |
| **PageHistory** | Version list/content `grid-cols-1 md:grid-cols-3` |
| **SpaceList** | Cards `grid-cols-1 md:grid-cols-2` |
| **SpaceSettings** | Single column `max-w-lg`, forms already stacked |

### Global mobile CSS (`index.css`)

- **Base font**: 16px with `-webkit-text-size-adjust: 100%` (prevents iOS zoom on input focus).
- **Tap targets**: `@media (pointer: coarse)` enforces `min-height: 44px` on buttons and selects.
- **Overflow prevention**: `html, body { overflow-x: hidden }`.
- **Momentum scroll**: `-webkit-overflow-scrolling: touch` on scroll containers.
- **Focus-visible**: 2px accent ring for keyboard navigation.
- **Word break**: Headings use `overflow-wrap: break-word` to prevent overflow.

### Customizing breakpoints

The sidebar drawer visibility is controlled by `lg:hidden` / `hidden lg:block` classes — change these to `md:` if you want the sidebar to appear earlier.

---

## Original Vite README

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

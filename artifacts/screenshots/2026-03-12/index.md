# Altassian Visual Review — 2026-03-12

Full-page screenshots captured with Playwright against local dev.

## Coverage Checklist

### 390px (mobile)

**Light mode:**

- [x] `390-login-default.png` — Login page
- [x] `390-signup-default.png` — Signup / Registration page
- [x] `390-landing-default.png` — Landing page
- [x] `390-dashboard-default.png` — Dashboard / Home
- [x] `390-spaces-list-default.png` — Spaces list
- [x] `390-spaces-create-default.png` — Create space form
- [x] `390-space-view-default.png` — Space view with page tree
- [x] `390-page-view-default.png` — Page content view
- [x] `390-editor-with-content.png` — TipTap editor with content
- [x] `390-editor-floating-toolbar.png` — Editor with floating/bubble toolbar
- [x] `390-editor-slash-menu.png` — Editor with slash command menu
- [x] `390-editor-empty.png` — Editor (empty new page)
- [x] `390-page-history-default.png` — Page version history
- [x] `390-search-empty.png` — Search page (empty state)
- [x] `390-search-results.png` — Search with results
- [x] `390-space-settings-default.png` — Space settings
- [x] `390-404-default.png` — 404 not-found page

**Dark mode:**

- [x] `390-login-dark.png` — Login page (dark)
- [x] `390-dashboard-dark.png` — Dashboard (dark)
- [x] `390-spaces-list-dark.png` — Spaces list (dark)
- [x] `390-space-view-dark.png` — Space view (dark)
- [x] `390-page-view-dark.png` — Page view (dark)
- [x] `390-editor-dark.png` — Editor (dark)
- [x] `390-search-dark.png` — Search results (dark)
- [x] `390-space-settings-dark.png` — Space settings (dark)

### 768px (tablet)

**Light mode:**

- [x] `768-login-default.png` — Login page
- [x] `768-signup-default.png` — Signup / Registration page
- [x] `768-landing-default.png` — Landing page
- [x] `768-dashboard-default.png` — Dashboard / Home
- [x] `768-spaces-list-default.png` — Spaces list
- [x] `768-spaces-create-default.png` — Create space form
- [x] `768-space-view-default.png` — Space view with page tree
- [x] `768-page-view-default.png` — Page content view
- [x] `768-editor-with-content.png` — TipTap editor with content
- [x] `768-editor-floating-toolbar.png` — Editor with floating/bubble toolbar
- [x] `768-editor-slash-menu.png` — Editor with slash command menu
- [x] `768-editor-empty.png` — Editor (empty new page)
- [x] `768-page-history-default.png` — Page version history
- [x] `768-search-empty.png` — Search page (empty state)
- [x] `768-search-results.png` — Search with results
- [x] `768-space-settings-default.png` — Space settings
- [x] `768-404-default.png` — 404 not-found page

**Dark mode:**

- [x] `768-login-dark.png` — Login page (dark)
- [x] `768-dashboard-dark.png` — Dashboard (dark)
- [x] `768-spaces-list-dark.png` — Spaces list (dark)
- [x] `768-space-view-dark.png` — Space view (dark)
- [x] `768-page-view-dark.png` — Page view (dark)
- [x] `768-editor-dark.png` — Editor (dark)
- [x] `768-search-dark.png` — Search results (dark)
- [x] `768-space-settings-dark.png` — Space settings (dark)

### 1280px (desktop)

**Light mode:**

- [x] `1280-login-default.png` — Login page
- [x] `1280-signup-default.png` — Signup / Registration page
- [x] `1280-landing-default.png` — Landing page
- [x] `1280-dashboard-default.png` — Dashboard / Home
- [x] `1280-spaces-list-default.png` — Spaces list
- [x] `1280-spaces-create-default.png` — Create space form
- [x] `1280-space-view-default.png` — Space view with page tree
- [x] `1280-page-view-default.png` — Page content view
- [x] `1280-page-view-sidebar-collapsed.png` — Page view with sidebar collapsed
- [x] `1280-editor-with-content.png` — TipTap editor with content
- [x] `1280-editor-floating-toolbar.png` — Editor with floating/bubble toolbar
- [x] `1280-editor-slash-menu.png` — Editor with slash command menu
- [x] `1280-editor-empty.png` — Editor (empty new page)
- [x] `1280-page-history-default.png` — Page version history
- [x] `1280-search-empty.png` — Search page (empty state)
- [x] `1280-search-results.png` — Search with results
- [x] `1280-space-settings-default.png` — Space settings
- [x] `1280-404-default.png` — 404 not-found page

**Dark mode:**

- [x] `1280-login-dark.png` — Login page (dark)
- [x] `1280-dashboard-dark.png` — Dashboard (dark)
- [x] `1280-spaces-list-dark.png` — Spaces list (dark)
- [x] `1280-space-view-dark.png` — Space view (dark)
- [x] `1280-page-view-dark.png` — Page view (dark)
- [x] `1280-editor-dark.png` — Editor (dark)
- [x] `1280-search-dark.png` — Search results (dark)
- [x] `1280-space-settings-dark.png` — Space settings (dark)

## Summary

- **Total screenshots:** 76
- **Captured:** 76

## Routes Covered

| Route | States |
|-------|--------|
| `/login` | default, dark |
| `/register` | default |
| `/landing` | default |
| `/` (dashboard) | default, dark |
| `/spaces` | list, dark |
| `/spaces/create` | form |
| `/spaces/:key` | page tree, dark, sidebar collapsed |
| `/spaces/:key/pages/:slug` | view, dark |
| `/spaces/:key/pages/:slug/edit` | content, floating toolbar, slash menu, dark |
| `/spaces/:key/pages/new` | empty editor |
| `/spaces/:key/pages/:slug/history` | version list |
| `/search` | empty, with results, dark |
| `/spaces/:key/settings` | default, dark |
| `/*` (404) | not-found |

## Breakpoints

- **390px** — iPhone 14 / small mobile
- **768px** — iPad / tablet portrait
- **1280px** — Standard laptop / desktop

## Visual Notes

- Dark mode toggled via `localStorage` + `data-theme` + `.dark` class
- Slash menu triggered by typing `/` in the editor
- Floating toolbar appears on text selection (Ctrl+A)
- Sidebar collapse captured where toggle button is available

## Gaps / Not Captured

- Password reset (route not implemented)
- Loading skeletons (transient, hard to capture reliably)
- Toast notifications (transient, appear on user actions)
- Profile/account settings (route not yet present)
- Attachment upload flow (requires file interaction)

---
*Generated 2026-03-12 by Playwright headless Chromium*

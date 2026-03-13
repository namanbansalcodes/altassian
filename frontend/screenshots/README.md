# Altassian Frontend — Visual Screenshots

Generated on 2026-03-12 using Playwright.

**Total screenshots: 64**

## Naming Convention

```
screenshots/<route>__<state>__<theme>__<breakpoint>.png
```

## Viewports

- **Desktop:** 1440×900
- **Mobile:** 390×844 (iPhone 14 Pro)

## Desktop — Light

| # | File | Description |
|---|------|-------------|
| 1 | `landing__default__light__desktop.png` | Landing / marketing page |
| 2 | `login__default__light__desktop.png` | Login form |
| 3 | `register__default__light__desktop.png` | Registration form |
| 4 | `dashboard__default__light__desktop.png` | Dashboard / home |
| 5 | `spaces__list__light__desktop.png` | All spaces list |
| 6 | `spaces__create-form__light__desktop.png` | Create new space form |
| 7 | `space-view__page-tree__light__desktop.png` | Space view with page tree sidebar |
| 8 | `page-view__default__light__desktop.png` | Page content view |
| 9 | `editor__toolbar__light__desktop.png` | TipTap editor with toolbar |
| 10 | `editor__bubble-menu__light__desktop.png` | Editor with bubble menu on selected text |
| 11 | `editor__slash-menu__light__desktop.png` | Editor slash command menu |
| 12 | `page-history__default__light__desktop.png` | Page version history |
| 13 | `search__empty__light__desktop.png` | Search page (empty) |
| 14 | `search__results__light__desktop.png` | Search results for "architecture" |
| 15 | `space-settings__default__light__desktop.png` | Space settings page |
| 16 | `404__default__light__desktop.png` | 404 not-found page |

## Desktop — Dark

| # | File | Description |
|---|------|-------------|
| 1 | `landing__default__dark__desktop.png` | Landing / marketing page |
| 2 | `login__default__dark__desktop.png` | Login form |
| 3 | `register__default__dark__desktop.png` | Registration form |
| 4 | `dashboard__default__dark__desktop.png` | Dashboard / home |
| 5 | `spaces__list__dark__desktop.png` | All spaces list |
| 6 | `spaces__create-form__dark__desktop.png` | Create new space form |
| 7 | `space-view__page-tree__dark__desktop.png` | Space view with page tree sidebar |
| 8 | `page-view__default__dark__desktop.png` | Page content view |
| 9 | `editor__toolbar__dark__desktop.png` | TipTap editor with toolbar |
| 10 | `editor__bubble-menu__dark__desktop.png` | Editor with bubble menu on selected text |
| 11 | `editor__slash-menu__dark__desktop.png` | Editor slash command menu |
| 12 | `page-history__default__dark__desktop.png` | Page version history |
| 13 | `search__empty__dark__desktop.png` | Search page (empty) |
| 14 | `search__results__dark__desktop.png` | Search results for "architecture" |
| 15 | `space-settings__default__dark__desktop.png` | Space settings page |
| 16 | `404__default__dark__desktop.png` | 404 not-found page |

## Mobile — Light

| # | File | Description |
|---|------|-------------|
| 1 | `landing__default__light__mobile.png` | Landing / marketing page |
| 2 | `login__default__light__mobile.png` | Login form |
| 3 | `register__default__light__mobile.png` | Registration form |
| 4 | `dashboard__default__light__mobile.png` | Dashboard / home |
| 5 | `spaces__list__light__mobile.png` | All spaces list |
| 6 | `spaces__create-form__light__mobile.png` | Create new space form |
| 7 | `space-view__page-tree__light__mobile.png` | Space view with page tree sidebar |
| 8 | `page-view__default__light__mobile.png` | Page content view |
| 9 | `editor__toolbar__light__mobile.png` | TipTap editor with toolbar |
| 10 | `editor__bubble-menu__light__mobile.png` | Editor with bubble menu on selected text |
| 11 | `editor__slash-menu__light__mobile.png` | Editor slash command menu |
| 12 | `page-history__default__light__mobile.png` | Page version history |
| 13 | `search__empty__light__mobile.png` | Search page (empty) |
| 14 | `search__results__light__mobile.png` | Search results for "architecture" |
| 15 | `space-settings__default__light__mobile.png` | Space settings page |
| 16 | `404__default__light__mobile.png` | 404 not-found page |

## Mobile — Dark

| # | File | Description |
|---|------|-------------|
| 1 | `landing__default__dark__mobile.png` | Landing / marketing page |
| 2 | `login__default__dark__mobile.png` | Login form |
| 3 | `register__default__dark__mobile.png` | Registration form |
| 4 | `dashboard__default__dark__mobile.png` | Dashboard / home |
| 5 | `spaces__list__dark__mobile.png` | All spaces list |
| 6 | `spaces__create-form__dark__mobile.png` | Create new space form |
| 7 | `space-view__page-tree__dark__mobile.png` | Space view with page tree sidebar |
| 8 | `page-view__default__dark__mobile.png` | Page content view |
| 9 | `editor__toolbar__dark__mobile.png` | TipTap editor with toolbar |
| 10 | `editor__bubble-menu__dark__mobile.png` | Editor with bubble menu on selected text |
| 11 | `editor__slash-menu__dark__mobile.png` | Editor slash command menu |
| 12 | `page-history__default__dark__mobile.png` | Page version history |
| 13 | `search__empty__dark__mobile.png` | Search page (empty) |
| 14 | `search__results__dark__mobile.png` | Search results for "architecture" |
| 15 | `space-settings__default__dark__mobile.png` | Space settings page |
| 16 | `404__default__dark__mobile.png` | 404 not-found page |

## Coverage

### Captured
- Landing page, Login, Registration (public routes)
- Dashboard / Home
- Spaces list, Create space form
- Space view with page tree sidebar
- Page content view
- TipTap editor: toolbar, bubble menu, slash command menu
- Page version history
- Search: empty state and results
- Space settings
- 404 not-found
- All of the above in both light and dark themes
- All of the above at both desktop (1440×900) and mobile (390×844) breakpoints

### Not yet captured (gaps)
- Profile / account settings (not yet implemented in frontend)
- Modal dialogs (delete confirmations render inline, not as modals)
- Loading skeletons (transient, appear <1s)
- Toast notifications (transient)
- Attachment upload flow

## How to regenerate

```bash
# 1. Start backend (port 8001)
cd altassian_backend && source venv/bin/activate
python manage.py migrate && python manage.py seed_demo
python manage.py runserver 0.0.0.0:8001

# 2. Start frontend (port 5173)
cd altassian_frontend && npm run dev

# 3. Capture screenshots
cd altassian_frontend && npx tsx scripts/screenshots-organized.ts
```

## Seed data

Screenshots require seed data. Run `python manage.py seed_demo` in the backend.
- **Users:** admin/AdminPass123, alice/Password123!, bob/Password123!
- **Spaces:** ENG (Engineering), PRD (Product), etc.
- **Pages:** Architecture Overview, API Reference, Development Setup, etc.

---

**To send to Naman on Telegram:** Share this `screenshots/` folder (or zip it) with Naman via Telegram.

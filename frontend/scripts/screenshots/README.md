# Screenshot Automation

Captures full-page screenshots of all primary Altassian frontend pages using Playwright.

## Prerequisites

- Backend running on `http://localhost:8001` (with demo seed data)
- Frontend dev server on `http://localhost:5173`
- Demo user `admin` / `Password123!`

## Run

```bash
# From the frontend root:
npx tsx scripts/screenshots.ts
```

## Output

Screenshots are saved to `screenshots/YYYY-MM-DD/` with these files:

| File | Page |
|------|------|
| 01-login.png | Login page |
| 02-dashboard.png | Dashboard / Home |
| 03-tree-light.png | Space page tree (light) |
| 04-tree-dark.png | Space page tree (dark) |
| 05-editor-light-toolbar.png | TipTap editor, light, floating toolbar |
| 06-editor-light-slash.png | TipTap editor, light, slash menu |
| 07-editor-dark-toolbar.png | TipTap editor, dark, floating toolbar |
| 08-editor-dark-slash.png | TipTap editor, dark, slash menu |
| 09-settings-light.png | Space settings (light) |
| 10-settings-dark.png | Space settings (dark) |
| 11-loading-skeleton.png | Loading skeleton state |
| 12-toast.png | Toast notification |

## Re-run

Delete the date folder and run again. Each run creates a new dated folder.

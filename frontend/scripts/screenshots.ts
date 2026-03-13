/**
 * Playwright screenshot script for Altassian frontend.
 *
 * Prerequisites:
 *   - Backend running on http://localhost:8001
 *   - Frontend running on http://localhost:5173
 *   - Demo user "admin" with password "AdminPass123"
 *   - Seed data loaded (python manage.py seed_demo)
 *
 * Usage:
 *   cd altassian_backend/frontend && npx tsx scripts/screenshots.ts
 *
 * Output:
 *   frontend/screenshots/{desktop,mobile,dark}/
 */

import { chromium, type Page, type Browser } from '@playwright/test'
import path from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const BASE = process.env.BASE_URL || 'http://localhost:5173'
const ROOT = path.resolve(__dirname, '..')
const OUT_BASE = path.join(ROOT, 'screenshots')
const DESKTOP_DIR = path.join(OUT_BASE, 'desktop')
const MOBILE_DIR = path.join(OUT_BASE, 'mobile')
const DARK_DIR = path.join(OUT_BASE, 'dark')

const CREDS = { username: 'admin', password: 'AdminPass123' }

const SPACE_KEY = 'ENG'
const PAGE_SLUG = 'architecture-overview'

const DESKTOP = { width: 1440, height: 900 }
const MOBILE = { width: 390, height: 844 }

interface ShotRecord {
  file: string
  folder: string
  description: string
}
const manifest: ShotRecord[] = []

function sleep(ms: number) {
  return new Promise(r => setTimeout(r, ms))
}

async function settle(page: Page) {
  await page.waitForLoadState('domcontentloaded').catch(() => {})
  await page.waitForFunction(() => (window as any).__APP_READY__ === true, { timeout: 15000 }).catch(() => {})
  await page.waitForLoadState('networkidle').catch(() => {})
  await sleep(800)
}

async function shot(page: Page, dir: string, folder: string, name: string, description: string) {
  await settle(page)
  const filePath = path.join(dir, name)
  await page.screenshot({ path: filePath, fullPage: true })
  manifest.push({ file: name, folder, description })
  console.log(`  ✓ ${folder}/${name}`)
}

async function setTheme(page: Page, theme: 'light' | 'dark') {
  await page.evaluate((t) => {
    localStorage.setItem('altassian-theme', t)
    document.documentElement.setAttribute('data-theme', t)
    if (t === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, theme)
  await sleep(400)
}

async function login(page: Page) {
  await page.goto(`${BASE}/login`)
  await settle(page)
  await page.fill('input[type="text"], input[name="username"]', CREDS.username)
  await page.fill('input[type="password"]', CREDS.password)
  await page.click('button[type="submit"]')
  await page.waitForURL('**/', { timeout: 15000 })
  await settle(page)
}

const editorSel = '.tiptap, .ProseMirror, [contenteditable="true"]'

async function captureDesktop(browser: Browser) {
  console.log('\n=== DESKTOP (1440×900, light) ===\n')
  const context = await browser.newContext({ viewport: DESKTOP, colorScheme: 'light' })
  const page = await context.newPage()

  // Public pages
  await page.goto(`${BASE}/landing`)
  await shot(page, DESKTOP_DIR, 'desktop', '01-landing_desktop.png', 'Landing / marketing page')

  await page.goto(`${BASE}/login`)
  await shot(page, DESKTOP_DIR, 'desktop', '02-login_desktop.png', 'Login page')

  await page.goto(`${BASE}/register`)
  await shot(page, DESKTOP_DIR, 'desktop', '03-register_desktop.png', 'Registration page')

  // Log in
  console.log('Logging in...')
  await login(page)

  // Authenticated pages
  await page.goto(`${BASE}/`)
  await shot(page, DESKTOP_DIR, 'desktop', '04-dashboard_desktop.png', 'Dashboard / home')

  await page.goto(`${BASE}/spaces`)
  await shot(page, DESKTOP_DIR, 'desktop', '05-spaces-list_desktop.png', 'Spaces list')

  await page.goto(`${BASE}/spaces/create`)
  await shot(page, DESKTOP_DIR, 'desktop', '06-create-space_desktop.png', 'Create new space form')

  await page.goto(`${BASE}/spaces/${SPACE_KEY}`)
  await shot(page, DESKTOP_DIR, 'desktop', '07-space-view_desktop.png', 'Space view with page tree')

  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}`)
  await shot(page, DESKTOP_DIR, 'desktop', '08-page-view_desktop.png', 'Page content view')

  // Editor - toolbar visible
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}/edit`)
  await settle(page)
  await page.waitForSelector(editorSel, { timeout: 10000 }).catch(() => {})
  await sleep(500)
  await shot(page, DESKTOP_DIR, 'desktop', '09-editor_desktop.png', 'TipTap rich-text editor with toolbar')

  // Editor - select text to show bubble menu
  const editorEl = page.locator(editorSel).first()
  if (await editorEl.count() > 0) {
    await editorEl.click()
    await sleep(200)
    await page.keyboard.press('Control+a')
    await sleep(600)
  }
  await shot(page, DESKTOP_DIR, 'desktop', '10-editor-bubble-menu_desktop.png', 'Editor with floating bubble toolbar')

  // Editor - slash menu
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}/edit`)
  await settle(page)
  await page.waitForSelector(editorSel, { timeout: 10000 }).catch(() => {})
  await sleep(500)
  const editorEl2 = page.locator(editorSel).first()
  if (await editorEl2.count() > 0) {
    await editorEl2.click()
    await sleep(200)
    await page.keyboard.press('End')
    await sleep(200)
    await page.keyboard.press('Enter')
    await sleep(200)
    await page.keyboard.type('/')
    await sleep(800)
  }
  await shot(page, DESKTOP_DIR, 'desktop', '11-editor-slash-menu_desktop.png', 'Editor slash command menu')

  // Page history
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}/history`)
  await shot(page, DESKTOP_DIR, 'desktop', '12-history_desktop.png', 'Page version history')

  // Search
  await page.goto(`${BASE}/search`)
  await settle(page)
  const searchInput = page.locator('input[type="search"], input[name="q"], input[placeholder*="earch"]').first()
  if (await searchInput.count() > 0) {
    await searchInput.fill('architecture')
    await page.keyboard.press('Enter')
  }
  await settle(page)
  await shot(page, DESKTOP_DIR, 'desktop', '13-search_desktop.png', 'Search results page')

  // Space settings
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/settings`)
  await shot(page, DESKTOP_DIR, 'desktop', '14-space-settings_desktop.png', 'Space settings')

  // 404
  await page.goto(`${BASE}/this-page-does-not-exist-404`)
  await shot(page, DESKTOP_DIR, 'desktop', '15-404_desktop.png', '404 not-found page')

  await context.close()
}

async function captureDark(browser: Browser) {
  console.log('\n=== DARK MODE (1440×900) ===\n')
  const context = await browser.newContext({ viewport: DESKTOP, colorScheme: 'dark' })
  const page = await context.newPage()

  // Set dark theme
  await page.goto(`${BASE}/login`)
  await setTheme(page, 'dark')

  await shot(page, DARK_DIR, 'dark', '01-login_dark.png', 'Login page (dark)')

  await login(page)
  await setTheme(page, 'dark')

  await page.goto(`${BASE}/`)
  await setTheme(page, 'dark')
  await shot(page, DARK_DIR, 'dark', '02-dashboard_dark.png', 'Dashboard (dark)')

  await page.goto(`${BASE}/spaces`)
  await setTheme(page, 'dark')
  await shot(page, DARK_DIR, 'dark', '03-spaces-list_dark.png', 'Spaces list (dark)')

  await page.goto(`${BASE}/spaces/${SPACE_KEY}`)
  await setTheme(page, 'dark')
  await shot(page, DARK_DIR, 'dark', '04-space-view_dark.png', 'Space view (dark)')

  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}`)
  await setTheme(page, 'dark')
  await shot(page, DARK_DIR, 'dark', '05-page-view_dark.png', 'Page view (dark)')

  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}/edit`)
  await settle(page)
  await page.waitForSelector(editorSel, { timeout: 10000 }).catch(() => {})
  await sleep(500)
  await setTheme(page, 'dark')
  await shot(page, DARK_DIR, 'dark', '06-editor_dark.png', 'TipTap editor (dark)')

  await page.goto(`${BASE}/spaces/${SPACE_KEY}/settings`)
  await setTheme(page, 'dark')
  await shot(page, DARK_DIR, 'dark', '07-space-settings_dark.png', 'Space settings (dark)')

  await page.goto(`${BASE}/search`)
  await settle(page)
  await setTheme(page, 'dark')
  const searchInput = page.locator('input[type="search"], input[name="q"], input[placeholder*="earch"]').first()
  if (await searchInput.count() > 0) {
    await searchInput.fill('architecture')
    await page.keyboard.press('Enter')
  }
  await settle(page)
  await shot(page, DARK_DIR, 'dark', '08-search_dark.png', 'Search results (dark)')

  await context.close()
}

async function captureMobile(browser: Browser) {
  console.log('\n=== MOBILE (390×844 — iPhone 12) ===\n')
  const context = await browser.newContext({
    viewport: MOBILE,
    colorScheme: 'light',
    isMobile: true,
    hasTouch: true,
  })
  const page = await context.newPage()

  // Login
  await page.goto(`${BASE}/login`)
  await shot(page, MOBILE_DIR, 'mobile', '01-login_mobile.png', 'Login page (mobile)')

  await login(page)

  // Dashboard
  await page.goto(`${BASE}/`)
  await shot(page, MOBILE_DIR, 'mobile', '02-dashboard_mobile.png', 'Dashboard (mobile)')

  // Spaces list
  await page.goto(`${BASE}/spaces`)
  await shot(page, MOBILE_DIR, 'mobile', '03-spaces-list_mobile.png', 'Spaces list (mobile)')

  // Space view
  await page.goto(`${BASE}/spaces/${SPACE_KEY}`)
  await shot(page, MOBILE_DIR, 'mobile', '04-space-view_mobile.png', 'Space view (mobile)')

  // Page view
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}`)
  await shot(page, MOBILE_DIR, 'mobile', '05-page-view_mobile.png', 'Page view (mobile)')

  // Editor
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}/edit`)
  await settle(page)
  await sleep(500)
  await shot(page, MOBILE_DIR, 'mobile', '06-editor_mobile.png', 'TipTap editor (mobile)')

  // Search
  await page.goto(`${BASE}/search`)
  await settle(page)
  const searchInput = page.locator('input[type="search"], input[name="q"], input[placeholder*="earch"]').first()
  if (await searchInput.count() > 0) {
    await searchInput.fill('architecture')
    await page.keyboard.press('Enter')
  }
  await settle(page)
  await shot(page, MOBILE_DIR, 'mobile', '07-search_mobile.png', 'Search results (mobile)')

  // Dark mobile dashboard
  await setTheme(page, 'dark')
  await page.goto(`${BASE}/`)
  await setTheme(page, 'dark')
  await shot(page, MOBILE_DIR, 'mobile', '08-dashboard_mobile_dark.png', 'Dashboard (mobile, dark)')

  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}`)
  await setTheme(page, 'dark')
  await shot(page, MOBILE_DIR, 'mobile', '09-page-view_mobile_dark.png', 'Page view (mobile, dark)')

  await context.close()
}

async function main() {
  // Create output directories
  for (const dir of [DESKTOP_DIR, MOBILE_DIR, DARK_DIR]) {
    fs.mkdirSync(dir, { recursive: true })
  }
  console.log(`Screenshots → ${OUT_BASE}\n`)

  const browser = await chromium.launch({ headless: true })

  await captureDesktop(browser)
  await captureDark(browser)
  await captureMobile(browser)

  await browser.close()

  // Group manifest by folder
  const desktopShots = manifest.filter(r => r.folder === 'desktop')
  const darkShots = manifest.filter(r => r.folder === 'dark')
  const mobileShots = manifest.filter(r => r.folder === 'mobile')

  const readme = [
    '# Altassian Frontend Screenshots',
    '',
    `Generated on ${new Date().toISOString().slice(0, 10)} using Playwright against local dev servers.`,
    '',
    '## Desktop (1440×900, light)',
    '',
    '| # | File | Description |',
    '|---|------|-------------|',
    ...desktopShots.map((r, i) => `| ${i + 1} | \`desktop/${r.file}\` | ${r.description} |`),
    '',
    '## Dark Mode (1440×900)',
    '',
    '| # | File | Description |',
    '|---|------|-------------|',
    ...darkShots.map((r, i) => `| ${i + 1} | \`dark/${r.file}\` | ${r.description} |`),
    '',
    '## Mobile (390×844, iPhone 12)',
    '',
    '| # | File | Description |',
    '|---|------|-------------|',
    ...mobileShots.map((r, i) => `| ${i + 1} | \`mobile/${r.file}\` | ${r.description} |`),
    '',
    '## Coverage',
    '',
    '### Captured',
    '- Landing page, Login, Registration (public)',
    '- Dashboard/Home, Spaces list, Create space form',
    '- Space view with page tree, Page content view',
    '- TipTap editor (toolbar, bubble menu, slash command menu)',
    '- Page version history, Search results, Space settings',
    '- 404 page',
    '- Dark mode variants for all key authenticated pages',
    '- Mobile viewport for login, dashboard, spaces, page view, editor, search',
    '',
    '### Not yet captured / gaps',
    '- Profile/account settings page (not yet implemented)',
    '- Modal dialogs (delete confirmation appears inline)',
    '- Loading skeletons (appear briefly, hard to capture reliably)',
    '- Toast notifications (transient)',
    '- Attachment upload flow',
    '',
    '## How to regenerate',
    '',
    '```bash',
    '# 1. Start backend (port 8001)',
    'cd altassian_backend && source venv/bin/activate',
    'python manage.py migrate && python manage.py seed_demo',
    'python manage.py runserver 0.0.0.0:8001',
    '',
    '# 2. Start frontend (port 5173)',
    'cd altassian_backend/frontend && npm run dev',
    '',
    '# 3. Run screenshot script',
    'cd altassian_backend/frontend && npx tsx scripts/screenshots.ts',
    '```',
    '',
    '## Seed data',
    '',
    'The screenshots require seed data. Run `python manage.py seed_demo` in the backend.',
    'This creates:',
    '- **Users:** admin/AdminPass123, alice/Password123!, bob/Password123!',
    '- **Spaces:** ENG (Engineering), PRD (Product), etc.',
    '- **Pages:** Architecture Overview, API Reference, Development Setup, etc.',
    '',
  ].join('\n')
  fs.writeFileSync(path.join(OUT_BASE, 'README.md'), readme)
  console.log(`\nDone! ${manifest.length} screenshots + README.md saved to ${OUT_BASE}`)
}

main().catch((err) => {
  console.error('Screenshot script failed:', err)
  process.exit(1)
})

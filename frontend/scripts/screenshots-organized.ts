/**
 * Comprehensive screenshot capture with organized naming.
 *
 * Naming: screenshots/<route>__<state>__<theme>__<breakpoint>.png
 *
 * Prerequisites:
 *   - Backend running on http://localhost:8001
 *   - Frontend running on http://localhost:5173
 *   - Seed data loaded (python manage.py seed_demo)
 */

import { chromium, type Page, type BrowserContext } from '@playwright/test'
import path from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const BASE = process.env.BASE_URL || 'http://localhost:5173'
const ROOT = path.resolve(__dirname, '..')
const OUT = path.join(ROOT, 'screenshots')

const CREDS = { username: 'admin', password: 'AdminPass123' }
const SPACE_KEY = 'ENG'
const PAGE_SLUG = 'architecture-overview'

const DESKTOP = { width: 1440, height: 900 }
const MOBILE = { width: 390, height: 844 }

type Theme = 'light' | 'dark'
type Breakpoint = 'desktop' | 'mobile'

interface ShotRecord {
  file: string
  route: string
  state: string
  theme: Theme
  breakpoint: Breakpoint
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

function shotName(route: string, state: string, theme: Theme, bp: Breakpoint): string {
  return `${route}__${state}__${theme}__${bp}.png`
}

async function shot(page: Page, route: string, state: string, theme: Theme, bp: Breakpoint, description: string) {
  await settle(page)
  const name = shotName(route, state, theme, bp)
  const filePath = path.join(OUT, name)
  await page.screenshot({ path: filePath, fullPage: true })
  manifest.push({ file: name, route, state, theme, breakpoint: bp, description })
  console.log(`  ✓ ${name}`)
}

async function setTheme(page: Page, theme: Theme) {
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

async function captureSet(browser: ReturnType<typeof chromium.launch> extends Promise<infer T> ? T : never, theme: Theme, bp: Breakpoint) {
  const viewport = bp === 'desktop' ? DESKTOP : MOBILE
  const isMobile = bp === 'mobile'
  const colorScheme = theme

  console.log(`\n=== ${bp.toUpperCase()} / ${theme.toUpperCase()} (${viewport.width}×${viewport.height}) ===\n`)

  const context = await browser.newContext({
    viewport,
    colorScheme,
    ...(isMobile ? { isMobile: true, hasTouch: true } : {}),
  })
  const page = await context.newPage()

  // --- Public pages ---

  // Landing
  await page.goto(`${BASE}/landing`)
  if (theme === 'dark') await setTheme(page, 'dark')
  await shot(page, 'landing', 'default', theme, bp, 'Landing / marketing page')

  // Login
  await page.goto(`${BASE}/login`)
  if (theme === 'dark') await setTheme(page, 'dark')
  await shot(page, 'login', 'default', theme, bp, 'Login form')

  // Register
  await page.goto(`${BASE}/register`)
  if (theme === 'dark') await setTheme(page, 'dark')
  await shot(page, 'register', 'default', theme, bp, 'Registration form')

  // --- Log in ---
  console.log('  Logging in...')
  await login(page)
  if (theme === 'dark') await setTheme(page, 'dark')

  // Dashboard
  await page.goto(`${BASE}/`)
  if (theme === 'dark') await setTheme(page, 'dark')
  await shot(page, 'dashboard', 'default', theme, bp, 'Dashboard / home')

  // Spaces list
  await page.goto(`${BASE}/spaces`)
  if (theme === 'dark') await setTheme(page, 'dark')
  await shot(page, 'spaces', 'list', theme, bp, 'All spaces list')

  // Create space
  await page.goto(`${BASE}/spaces/create`)
  if (theme === 'dark') await setTheme(page, 'dark')
  await shot(page, 'spaces', 'create-form', theme, bp, 'Create new space form')

  // Space view (page tree)
  await page.goto(`${BASE}/spaces/${SPACE_KEY}`)
  if (theme === 'dark') await setTheme(page, 'dark')
  await shot(page, 'space-view', 'page-tree', theme, bp, 'Space view with page tree sidebar')

  // Page view
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}`)
  if (theme === 'dark') await setTheme(page, 'dark')
  await shot(page, 'page-view', 'default', theme, bp, 'Page content view')

  // Editor - toolbar
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}/edit`)
  await settle(page)
  await page.waitForSelector(editorSel, { timeout: 10000 }).catch(() => {})
  await sleep(500)
  if (theme === 'dark') await setTheme(page, 'dark')
  await shot(page, 'editor', 'toolbar', theme, bp, 'TipTap editor with toolbar')

  // Editor - bubble menu (select text)
  const editorEl = page.locator(editorSel).first()
  if (await editorEl.count() > 0) {
    await editorEl.click()
    await sleep(200)
    await page.keyboard.press('Control+a')
    await sleep(600)
  }
  await shot(page, 'editor', 'bubble-menu', theme, bp, 'Editor with bubble menu on selected text')

  // Editor - slash menu
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}/edit`)
  await settle(page)
  await page.waitForSelector(editorSel, { timeout: 10000 }).catch(() => {})
  await sleep(500)
  if (theme === 'dark') await setTheme(page, 'dark')
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
  await shot(page, 'editor', 'slash-menu', theme, bp, 'Editor slash command menu')

  // Page history
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}/history`)
  if (theme === 'dark') await setTheme(page, 'dark')
  await shot(page, 'page-history', 'default', theme, bp, 'Page version history')

  // Search - empty
  await page.goto(`${BASE}/search`)
  await settle(page)
  if (theme === 'dark') await setTheme(page, 'dark')
  await shot(page, 'search', 'empty', theme, bp, 'Search page (empty)')

  // Search - with results
  const searchInput = page.locator('input[type="search"], input[name="q"], input[placeholder*="earch"]').first()
  if (await searchInput.count() > 0) {
    await searchInput.fill('architecture')
    await page.keyboard.press('Enter')
  }
  await settle(page)
  await shot(page, 'search', 'results', theme, bp, 'Search results for "architecture"')

  // Space settings
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/settings`)
  if (theme === 'dark') await setTheme(page, 'dark')
  await shot(page, 'space-settings', 'default', theme, bp, 'Space settings page')

  // 404
  await page.goto(`${BASE}/this-page-does-not-exist-404`)
  if (theme === 'dark') await setTheme(page, 'dark')
  await shot(page, '404', 'default', theme, bp, '404 not-found page')

  await context.close()
}

async function main() {
  // Clean and create output dir
  if (fs.existsSync(OUT)) {
    // Remove old PNGs (keep README if present)
    for (const f of fs.readdirSync(OUT)) {
      const fp = path.join(OUT, f)
      if (fs.statSync(fp).isFile() && f.endsWith('.png')) {
        fs.unlinkSync(fp)
      }
      if (fs.statSync(fp).isDirectory()) {
        fs.rmSync(fp, { recursive: true })
      }
    }
  }
  fs.mkdirSync(OUT, { recursive: true })

  console.log(`Screenshots → ${OUT}\n`)

  const browser = await chromium.launch({ headless: true })

  // Capture all 4 combinations
  await captureSet(browser, 'light', 'desktop')
  await captureSet(browser, 'dark', 'desktop')
  await captureSet(browser, 'light', 'mobile')
  await captureSet(browser, 'dark', 'mobile')

  await browser.close()

  // --- Generate README ---
  const groups: Record<string, ShotRecord[]> = {
    'Desktop — Light': manifest.filter(r => r.breakpoint === 'desktop' && r.theme === 'light'),
    'Desktop — Dark': manifest.filter(r => r.breakpoint === 'desktop' && r.theme === 'dark'),
    'Mobile — Light': manifest.filter(r => r.breakpoint === 'mobile' && r.theme === 'light'),
    'Mobile — Dark': manifest.filter(r => r.breakpoint === 'mobile' && r.theme === 'dark'),
  }

  const lines: string[] = [
    '# Altassian Frontend — Visual Screenshots',
    '',
    `Generated on ${new Date().toISOString().slice(0, 10)} using Playwright.`,
    '',
    `**Total screenshots: ${manifest.length}**`,
    '',
    '## Naming Convention',
    '',
    '```',
    'screenshots/<route>__<state>__<theme>__<breakpoint>.png',
    '```',
    '',
    '## Viewports',
    '',
    `- **Desktop:** ${DESKTOP.width}×${DESKTOP.height}`,
    `- **Mobile:** ${MOBILE.width}×${MOBILE.height} (iPhone 14 Pro)`,
    '',
  ]

  for (const [title, shots] of Object.entries(groups)) {
    lines.push(`## ${title}`, '')
    lines.push('| # | File | Description |')
    lines.push('|---|------|-------------|')
    shots.forEach((r, i) => {
      lines.push(`| ${i + 1} | \`${r.file}\` | ${r.description} |`)
    })
    lines.push('')
  }

  lines.push(
    '## Coverage',
    '',
    '### Captured',
    '- Landing page, Login, Registration (public routes)',
    '- Dashboard / Home',
    '- Spaces list, Create space form',
    '- Space view with page tree sidebar',
    '- Page content view',
    '- TipTap editor: toolbar, bubble menu, slash command menu',
    '- Page version history',
    '- Search: empty state and results',
    '- Space settings',
    '- 404 not-found',
    '- All of the above in both light and dark themes',
    '- All of the above at both desktop (1440×900) and mobile (390×844) breakpoints',
    '',
    '### Not yet captured (gaps)',
    '- Profile / account settings (not yet implemented in frontend)',
    '- Modal dialogs (delete confirmations render inline, not as modals)',
    '- Loading skeletons (transient, appear <1s)',
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
    'cd altassian_frontend && npm run dev',
    '',
    '# 3. Capture screenshots',
    'cd altassian_frontend && npx tsx scripts/screenshots-organized.ts',
    '```',
    '',
    '## Seed data',
    '',
    'Screenshots require seed data. Run `python manage.py seed_demo` in the backend.',
    '- **Users:** admin/AdminPass123, alice/Password123!, bob/Password123!',
    '- **Spaces:** ENG (Engineering), PRD (Product), etc.',
    '- **Pages:** Architecture Overview, API Reference, Development Setup, etc.',
    '',
    '---',
    '',
    '**To send to Naman on Telegram:** Share this `screenshots/` folder (or zip it) with Naman via Telegram.',
    '',
  )

  fs.writeFileSync(path.join(OUT, 'README.md'), lines.join('\n'))
  console.log(`\nDone! ${manifest.length} screenshots + README.md → ${OUT}`)
}

main().catch((err) => {
  console.error('Screenshot script failed:', err)
  process.exit(1)
})

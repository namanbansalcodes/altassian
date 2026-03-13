/**
 * Visual QA Pack — Comprehensive screenshot capture.
 *
 * Output: screenshots/20260313/[page]/[breakpoint]/[theme].png
 * Breakpoints: 375x812 (mobile), 768x1024 (tablet), 1280x800 (desktop), 1600x900 (widescreen)
 * Themes: light, dark
 *
 * Prerequisites:
 *   - Backend running on http://localhost:8001
 *   - Frontend running on http://localhost:5173
 *   - Seed data loaded (python manage.py seed_demo)
 */

import { chromium, type Page, type Browser } from '@playwright/test'
import path from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const BASE = process.env.BASE_URL || 'http://localhost:5173'
const ROOT = path.resolve(__dirname, '..')
const DATE = '20260313'
const OUT = path.join(ROOT, 'screenshots', DATE)

const CREDS = { username: 'admin', password: 'AdminPass123' }
const SPACE_KEY = 'ENG'
const PAGE_SLUG = 'architecture-overview'
const ALT_PAGE_SLUG = 'development-setup'

type Theme = 'light' | 'dark'

interface Viewport {
  label: string
  width: number
  height: number
  isMobile: boolean
}

const VIEWPORTS: Viewport[] = [
  { label: '375x812', width: 375, height: 812, isMobile: true },
  { label: '768x1024', width: 768, height: 1024, isMobile: false },
  { label: '1280x800', width: 1280, height: 800, isMobile: false },
  { label: '1600x900', width: 1600, height: 900, isMobile: false },
]

const THEMES: Theme[] = ['light', 'dark']

interface ShotRecord {
  page: string
  breakpoint: string
  theme: Theme
  file: string
  description: string
  captured: boolean
  note?: string
}

const manifest: ShotRecord[] = []

function sleep(ms: number): Promise<void> {
  return new Promise(r => setTimeout(r, ms))
}

async function settle(page: Page): Promise<void> {
  await page.waitForLoadState('domcontentloaded').catch(() => {})
  await page.waitForFunction(() => (window as any).__APP_READY__ === true, { timeout: 12000 }).catch(() => {})
  await page.waitForLoadState('networkidle').catch(() => {})
  await sleep(800)
}

function ensureDir(dir: string): void {
  fs.mkdirSync(dir, { recursive: true })
}

async function shot(
  page: Page,
  pageName: string,
  breakpoint: string,
  theme: Theme,
  description: string,
): Promise<void> {
  await settle(page)
  const dir = path.join(OUT, pageName, breakpoint)
  ensureDir(dir)
  const filePath = path.join(dir, `${theme}.png`)
  const relPath = `${pageName}/${breakpoint}/${theme}.png`
  try {
    await page.screenshot({ path: filePath, fullPage: true })
    manifest.push({ page: pageName, breakpoint, theme, file: relPath, description, captured: true })
    console.log(`  ✓ ${relPath}`)
  } catch (e: any) {
    manifest.push({ page: pageName, breakpoint, theme, file: relPath, description, captured: false, note: e.message?.slice(0, 100) })
    console.log(`  ✗ ${relPath} — ${e.message?.slice(0, 80)}`)
  }
}

async function setTheme(page: Page, theme: Theme): Promise<void> {
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

async function login(page: Page): Promise<void> {
  await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded' })
  await settle(page)
  await page.fill('input[type="text"], input[name="username"]', CREDS.username)
  await page.fill('input[type="password"]', CREDS.password)
  await page.click('button[type="submit"]')
  await page.waitForURL('**/', { timeout: 15000 }).catch(() => {})
  await settle(page)
}

const editorSel = '.tiptap, .ProseMirror, [contenteditable="true"]'

async function findPageSlug(page: Page): Promise<string> {
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}`, { waitUntil: 'domcontentloaded' })
  await sleep(1500)
  const content = await page.textContent('body').catch(() => '')
  if (content && !content.includes('Not Found') && !content.includes('404') && content.length > 200) {
    return PAGE_SLUG
  }
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${ALT_PAGE_SLUG}`, { waitUntil: 'domcontentloaded' })
  await sleep(1500)
  const content2 = await page.textContent('body').catch(() => '')
  if (content2 && !content2.includes('Not Found') && content2.length > 200) {
    return ALT_PAGE_SLUG
  }
  return PAGE_SLUG
}

async function captureAll(browser: Browser, vp: Viewport, theme: Theme): Promise<void> {
  const bp = vp.label
  console.log(`\n=== ${bp} / ${theme.toUpperCase()} ===\n`)

  const ctx = await browser.newContext({
    viewport: { width: vp.width, height: vp.height },
    colorScheme: theme,
    isMobile: vp.isMobile,
    hasTouch: vp.isMobile,
  })
  const page = await ctx.newPage()

  const applyTheme = async () => { if (theme === 'dark') await setTheme(page, 'dark') }

  // --- Public pages ---

  // Landing
  await page.goto(`${BASE}/landing`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await shot(page, 'landing', bp, theme, 'Landing / marketing page')

  // Login
  await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await shot(page, 'login', bp, theme, 'Login form')

  // Register
  await page.goto(`${BASE}/register`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await shot(page, 'register', bp, theme, 'Registration form')

  // --- Log in ---
  console.log('  Logging in...')
  await login(page)
  await applyTheme()

  // Dashboard
  await page.goto(`${BASE}/`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await shot(page, 'dashboard', bp, theme, 'Dashboard / home')

  // Spaces list
  await page.goto(`${BASE}/spaces`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await shot(page, 'spaces-list', bp, theme, 'All spaces list')

  // Create space
  await page.goto(`${BASE}/spaces/create`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await shot(page, 'create-space', bp, theme, 'Create new space form')

  // Space view (page tree)
  await page.goto(`${BASE}/spaces/${SPACE_KEY}`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await shot(page, 'space-view', bp, theme, 'Space view with page tree sidebar')

  // Find page slug
  const slug = await findPageSlug(page)
  console.log(`  Using page slug: ${slug}`)

  // Page view
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${slug}`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await shot(page, 'page-view', bp, theme, 'Page content view')

  // Sidebar collapsed (desktop+ only)
  if (vp.width >= 1024) {
    try {
      const toggle = page.locator('button[aria-label*="ollapse"], button[aria-label*="Sidebar"], button[aria-label*="sidebar"]').first()
      if (await toggle.isVisible({ timeout: 3000 }).catch(() => false)) {
        await toggle.click()
        await sleep(600)
        await shot(page, 'page-view-sidebar-collapsed', bp, theme, 'Page view with sidebar collapsed')
        await toggle.click().catch(() => {})
        await sleep(400)
      }
    } catch {
      console.log('  ⊘ Sidebar toggle not available')
    }
  }

  // --- Editor states ---

  // Editor with content
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${slug}/edit`, { waitUntil: 'domcontentloaded' })
  await settle(page)
  await page.waitForSelector(editorSel, { timeout: 10000 }).catch(() => {})
  await sleep(500)
  await applyTheme()
  await shot(page, 'editor-main', bp, theme, 'TipTap editor with content')

  // Editor bubble menu (select all text)
  const editorEl = page.locator(editorSel).first()
  if (await editorEl.count() > 0) {
    await editorEl.click()
    await sleep(200)
    await page.keyboard.press('Control+a')
    await sleep(800)
    await shot(page, 'editor-bubble-menu', bp, theme, 'Editor with floating bubble toolbar')
  }

  // Editor slash menu
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${slug}/edit`, { waitUntil: 'domcontentloaded' })
  await settle(page)
  await page.waitForSelector(editorSel, { timeout: 10000 }).catch(() => {})
  await sleep(500)
  await applyTheme()
  const editorEl2 = page.locator(editorSel).first()
  if (await editorEl2.count() > 0) {
    await editorEl2.click()
    await sleep(200)
    await page.keyboard.press('End')
    await sleep(200)
    await page.keyboard.press('Enter')
    await sleep(200)
    await page.keyboard.type('/')
    await sleep(1000)
  }
  await shot(page, 'editor-slash-menu', bp, theme, 'Editor slash command menu open')

  // Editor empty (new page)
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/new`, { waitUntil: 'domcontentloaded' })
  await settle(page)
  await page.waitForSelector(editorSel, { timeout: 10000 }).catch(() => {})
  await sleep(500)
  await applyTheme()
  await shot(page, 'editor-empty', bp, theme, 'Editor (empty new page)')

  // Page history
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${slug}/history`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await shot(page, 'page-history', bp, theme, 'Page version history')

  // Search empty
  await page.goto(`${BASE}/search`, { waitUntil: 'domcontentloaded' })
  await settle(page)
  await applyTheme()
  await shot(page, 'search-empty', bp, theme, 'Search page (empty state)')

  // Search with results
  const searchInput = page.locator('input[type="search"], input[name="q"], input[placeholder*="earch"]').first()
  if (await searchInput.count() > 0) {
    await searchInput.fill('architecture')
    await page.keyboard.press('Enter')
  }
  await settle(page)
  await shot(page, 'search-results', bp, theme, 'Search results for "architecture"')

  // Space settings
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/settings`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await shot(page, 'space-settings', bp, theme, 'Space settings page')

  // 404
  await page.goto(`${BASE}/this-page-does-not-exist-404`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await shot(page, '404', bp, theme, '404 not-found page')

  await ctx.close()
}

function generateIndex(): void {
  const lines: string[] = [
    `# Altassian Visual QA Pack — ${DATE}`,
    '',
    'Comprehensive screenshots captured with Playwright for visual review.',
    '',
    '## Breakpoints',
    '',
    '| Label | Resolution | Type |',
    '|-------|-----------|------|',
    '| 375x812 | 375×812 | Mobile (iPhone) |',
    '| 768x1024 | 768×1024 | Tablet (iPad) |',
    '| 1280x800 | 1280×800 | Desktop |',
    '| 1600x900 | 1600×900 | Widescreen |',
    '',
    '## Pages & Screenshots',
    '',
  ]

  // Group by page name
  const pages = [...new Set(manifest.map(r => r.page))]

  for (const pg of pages) {
    const pgShots = manifest.filter(r => r.page === pg)
    const desc = pgShots[0]?.description || pg
    lines.push(`### ${pg}`)
    lines.push(`> ${desc}`)
    lines.push('')

    for (const vp of VIEWPORTS) {
      const vpShots = pgShots.filter(r => r.breakpoint === vp.label)
      if (vpShots.length === 0) continue

      for (const s of vpShots) {
        const check = s.captured ? 'x' : ' '
        const note = s.note ? ` ⚠ ${s.note}` : ''
        lines.push(`- [${check}] \`${s.file}\`${note}`)
      }
    }
    lines.push('')
  }

  // Summary
  const captured = manifest.filter(r => r.captured).length
  const failed = manifest.filter(r => !r.captured).length

  lines.push('## Summary')
  lines.push('')
  lines.push(`- **Total:** ${manifest.length}`)
  lines.push(`- **Captured:** ${captured}`)
  if (failed > 0) lines.push(`- **Failed:** ${failed}`)
  lines.push(`- **Pages:** ${pages.length}`)
  lines.push(`- **Breakpoints:** ${VIEWPORTS.map(v => v.label).join(', ')}`)
  lines.push(`- **Themes:** light, dark`)
  lines.push('')

  lines.push('## Routes Covered')
  lines.push('')
  lines.push('| Route | Page Name | States |')
  lines.push('|-------|-----------|--------|')
  lines.push('| `/landing` | landing | default |')
  lines.push('| `/login` | login | default |')
  lines.push('| `/register` | register | default |')
  lines.push('| `/` | dashboard | default |')
  lines.push('| `/spaces` | spaces-list | default |')
  lines.push('| `/spaces/create` | create-space | form |')
  lines.push('| `/spaces/:key` | space-view | page tree |')
  lines.push('| `/spaces/:key/pages/:slug` | page-view | default, sidebar-collapsed |')
  lines.push('| `/spaces/:key/pages/:slug/edit` | editor-main | content, bubble-menu, slash-menu |')
  lines.push('| `/spaces/:key/pages/new` | editor-empty | empty |')
  lines.push('| `/spaces/:key/pages/:slug/history` | page-history | default |')
  lines.push('| `/search` | search-empty, search-results | empty, results |')
  lines.push('| `/spaces/:key/settings` | space-settings | default |')
  lines.push('| `/*` | 404 | not-found |')
  lines.push('')

  // TODOs / gaps
  lines.push('## TODO — Gaps & Missing')
  lines.push('')
  lines.push('- [ ] Profile/account settings — route not yet implemented in frontend')
  lines.push('- [ ] Loading skeleton states — transient, appear <1s, hard to capture reliably')
  lines.push('- [ ] Toast notifications — transient, triggered by user actions')
  lines.push('- [ ] Attachment upload flow — requires file picker interaction')
  lines.push('- [ ] Password reset page — route not implemented')
  lines.push('- [ ] Delete confirmation modals — rendered inline, not as modal overlays')
  lines.push('')

  lines.push('---')
  lines.push(`*Generated ${DATE} by Playwright headless Chromium*`)
  lines.push('')

  fs.writeFileSync(path.join(OUT, 'index.md'), lines.join('\n'))
  console.log(`\n✓ index.md written to ${OUT}/index.md`)
}

async function main(): Promise<void> {
  // Clean output dir if it exists
  if (fs.existsSync(OUT)) {
    fs.rmSync(OUT, { recursive: true })
  }
  ensureDir(OUT)

  console.log(`Screenshots → ${OUT}\n`)

  const browser = await chromium.launch({ headless: true })

  try {
    for (const vp of VIEWPORTS) {
      for (const theme of THEMES) {
        await captureAll(browser, vp, theme)
      }
    }
  } finally {
    await browser.close()
  }

  generateIndex()

  const captured = manifest.filter(r => r.captured).length
  console.log(`\nDone! ${captured}/${manifest.length} screenshots saved to ${OUT}`)
}

main().catch((err) => {
  console.error('Screenshot capture failed:', err)
  process.exit(1)
})

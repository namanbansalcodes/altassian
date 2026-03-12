/**
 * Comprehensive Playwright screenshot capture for Altassian.
 *
 * Breakpoints: 390px (mobile), 768px (tablet), 1280px (desktop)
 * Naming: <breakpoint>-<route>-<state>.png
 *
 * Prerequisites:
 *   - Backend on http://localhost:8001
 *   - Frontend on http://localhost:5173
 *   - Demo data seeded
 *
 * Usage:
 *   npx tsx capture.ts
 */

import { chromium, type Page, type Browser, type BrowserContext } from '@playwright/test'
import path from 'path'
import fs from 'fs'

const BASE = process.env.BASE_URL || 'http://localhost:5173'
const TODAY = '2026-03-12'
const OUT_DIR = '/home/namanbansal/.openclaw/workspace/artifacts/screenshots/2026-03-12'

const CREDS = { username: 'admin', password: 'AdminPass123' }

const SPACE_KEY = 'ENG'
const PAGE_SLUG = 'architecture-overview'  // has rich content
const ALT_PAGE_SLUG = 'development-setup'  // fallback

interface Viewport {
  label: string
  width: number
  height: number
  isMobile?: boolean
}

const VIEWPORTS: Viewport[] = [
  { label: '390', width: 390, height: 844, isMobile: true },
  { label: '768', width: 768, height: 1024, isMobile: false },
  { label: '1280', width: 1280, height: 900, isMobile: false },
]

interface ShotRecord {
  file: string
  description: string
  viewport: string
  theme: string
  captured: boolean
  note?: string
}
const manifest: ShotRecord[] = []

function sleep(ms: number): Promise<void> {
  return new Promise(r => setTimeout(r, ms))
}

async function settle(page: Page): Promise<void> {
  await page.waitForLoadState('domcontentloaded').catch(() => {})
  await page.waitForFunction(() => (window as any).__APP_READY__ === true, { timeout: 10000 }).catch(() => {})
  await page.waitForLoadState('networkidle').catch(() => {})
  await sleep(1000)
}

async function shot(page: Page, name: string, description: string, vpLabel: string, theme: string): Promise<void> {
  await settle(page)
  const filePath = path.join(OUT_DIR, name)
  try {
    await page.screenshot({ path: filePath, fullPage: true })
    manifest.push({ file: name, description, viewport: vpLabel, theme, captured: true })
    console.log(`  ✓ ${name}`)
  } catch (e: any) {
    manifest.push({ file: name, description, viewport: vpLabel, theme, captured: false, note: e.message?.slice(0, 100) })
    console.log(`  ✗ ${name} — ${e.message?.slice(0, 80)}`)
  }
}

async function setDarkTheme(page: Page): Promise<void> {
  await page.evaluate(() => {
    localStorage.setItem('altassian-theme', 'dark')
    document.documentElement.setAttribute('data-theme', 'dark')
    document.documentElement.classList.add('dark')
  })
  await sleep(500)
}

async function setLightTheme(page: Page): Promise<void> {
  await page.evaluate(() => {
    localStorage.setItem('altassian-theme', 'light')
    document.documentElement.setAttribute('data-theme', 'light')
    document.documentElement.classList.remove('dark')
  })
  await sleep(300)
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

// Find which page slug actually exists
async function findPageSlug(page: Page): Promise<string> {
  // Try the preferred slug first
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}`, { waitUntil: 'domcontentloaded' })
  await sleep(1500)
  const url = page.url()
  if (!url.includes('404') && !url.includes('not-found')) {
    const content = await page.textContent('body').catch(() => '')
    if (content && !content.includes('Not Found') && !content.includes('404') && content.length > 200) {
      return PAGE_SLUG
    }
  }
  // Try alternate
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${ALT_PAGE_SLUG}`, { waitUntil: 'domcontentloaded' })
  await sleep(1500)
  const content2 = await page.textContent('body').catch(() => '')
  if (content2 && !content2.includes('Not Found') && content2.length > 200) {
    return ALT_PAGE_SLUG
  }
  // Try to find any page slug from the space view
  await page.goto(`${BASE}/spaces/${SPACE_KEY}`, { waitUntil: 'domcontentloaded' })
  await settle(page)
  const links = await page.$$eval('a[href*="/pages/"]', (els: HTMLAnchorElement[]) =>
    els.map(el => el.href).filter(h => h.includes(`/spaces/${(window as any).__SPACE_KEY || 'ENG'}/pages/`))
  )
  if (links.length > 0) {
    const match = links[0].match(/\/pages\/([^/]+)/)
    if (match) return match[1]
  }
  return ALT_PAGE_SLUG // fallback
}

// ─── Light mode captures at a given viewport ────────────────────────

async function captureLightAtViewport(browser: Browser, vp: Viewport): Promise<void> {
  const prefix = vp.label
  console.log(`\n=== ${prefix}px — LIGHT MODE ===\n`)

  const ctx = await browser.newContext({
    viewport: { width: vp.width, height: vp.height },
    colorScheme: 'light',
    isMobile: vp.isMobile,
    hasTouch: vp.isMobile,
  })
  const page = await ctx.newPage()

  // --- Auth pages (unauthenticated) ---

  // Login
  await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded' })
  await shot(page, `${prefix}-login-default.png`, 'Login page', prefix, 'light')

  // Register / Signup
  await page.goto(`${BASE}/register`, { waitUntil: 'domcontentloaded' })
  await shot(page, `${prefix}-signup-default.png`, 'Signup / Registration page', prefix, 'light')

  // Landing page
  await page.goto(`${BASE}/landing`, { waitUntil: 'domcontentloaded' })
  await shot(page, `${prefix}-landing-default.png`, 'Landing page', prefix, 'light')

  // --- Log in ---
  console.log(`  Logging in at ${prefix}px...`)
  await login(page)

  // Dashboard
  await page.goto(`${BASE}/`, { waitUntil: 'domcontentloaded' })
  await shot(page, `${prefix}-dashboard-default.png`, 'Dashboard / Home', prefix, 'light')

  // Spaces list
  await page.goto(`${BASE}/spaces`, { waitUntil: 'domcontentloaded' })
  await shot(page, `${prefix}-spaces-list-default.png`, 'Spaces list', prefix, 'light')

  // Create space
  await page.goto(`${BASE}/spaces/create`, { waitUntil: 'domcontentloaded' })
  await shot(page, `${prefix}-spaces-create-default.png`, 'Create space form', prefix, 'light')

  // Space view (page tree)
  await page.goto(`${BASE}/spaces/${SPACE_KEY}`, { waitUntil: 'domcontentloaded' })
  await shot(page, `${prefix}-space-view-default.png`, 'Space view with page tree', prefix, 'light')

  // Find a valid page slug
  const slug = await findPageSlug(page)
  console.log(`  Using page slug: ${slug}`)

  // Page view
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${slug}`, { waitUntil: 'domcontentloaded' })
  await shot(page, `${prefix}-page-view-default.png`, 'Page content view', prefix, 'light')

  // --- Sidebar collapsed/expanded (desktop only — toggle hidden below lg/1024px) ---
  if (vp.width >= 1024) {
    try {
      const sidebarToggle = page.locator('button[aria-label*="ollapse sidebar"], button[aria-label*="Sidebar"]').first()
      if (await sidebarToggle.isVisible({ timeout: 3000 }).catch(() => false)) {
        await sidebarToggle.click()
        await sleep(600)
        await shot(page, `${prefix}-page-view-sidebar-collapsed.png`, 'Page view with sidebar collapsed', prefix, 'light')
        await sidebarToggle.click().catch(() => {})
        await sleep(500)
      }
    } catch {
      console.log(`  ⊘ Sidebar toggle not available at ${prefix}px`)
    }
  }

  // --- Editor with content ---
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${slug}/edit`, { waitUntil: 'domcontentloaded' })
  await settle(page)
  await page.waitForSelector(editorSel, { timeout: 10000 }).catch(() => {})
  await sleep(800)
  await shot(page, `${prefix}-editor-with-content.png`, 'TipTap editor with content', prefix, 'light')

  // --- Editor: floating toolbar (select text) ---
  const editorEl = page.locator(editorSel).first()
  if (await editorEl.count() > 0) {
    await editorEl.click()
    await sleep(200)
    await page.keyboard.press('Control+a')
    await sleep(800)
    await shot(page, `${prefix}-editor-floating-toolbar.png`, 'Editor with floating/bubble toolbar', prefix, 'light')
  }

  // --- Editor: slash menu ---
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${slug}/edit`, { waitUntil: 'domcontentloaded' })
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
    await sleep(1000)
  }
  await shot(page, `${prefix}-editor-slash-menu.png`, 'Editor with slash command menu', prefix, 'light')

  // --- Editor: empty new page ---
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/new`, { waitUntil: 'domcontentloaded' })
  await settle(page)
  await page.waitForSelector(editorSel, { timeout: 10000 }).catch(() => {})
  await sleep(500)
  await shot(page, `${prefix}-editor-empty.png`, 'Editor (empty new page)', prefix, 'light')

  // Page history
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${slug}/history`, { waitUntil: 'domcontentloaded' })
  await shot(page, `${prefix}-page-history-default.png`, 'Page version history', prefix, 'light')

  // Search (empty)
  await page.goto(`${BASE}/search`, { waitUntil: 'domcontentloaded' })
  await settle(page)
  await shot(page, `${prefix}-search-empty.png`, 'Search page (empty state)', prefix, 'light')

  // Search (with results)
  const searchInput = page.locator('input[type="search"], input[name="q"], input[placeholder*="earch"]').first()
  if (await searchInput.count() > 0) {
    await searchInput.fill('architecture')
    await page.keyboard.press('Enter')
  }
  await settle(page)
  await shot(page, `${prefix}-search-results.png`, 'Search with results', prefix, 'light')

  // Space settings
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/settings`, { waitUntil: 'domcontentloaded' })
  await shot(page, `${prefix}-space-settings-default.png`, 'Space settings', prefix, 'light')

  // 404 page
  await page.goto(`${BASE}/nonexistent-route-404`, { waitUntil: 'domcontentloaded' })
  await shot(page, `${prefix}-404-default.png`, '404 not-found page', prefix, 'light')

  await ctx.close()
}

// ─── Dark mode captures at a given viewport ─────────────────────────

async function captureDarkAtViewport(browser: Browser, vp: Viewport): Promise<void> {
  const prefix = vp.label
  console.log(`\n=== ${prefix}px — DARK MODE ===\n`)

  const ctx = await browser.newContext({
    viewport: { width: vp.width, height: vp.height },
    colorScheme: 'dark',
    isMobile: vp.isMobile,
    hasTouch: vp.isMobile,
  })
  const page = await ctx.newPage()

  // Login dark
  await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded' })
  await setDarkTheme(page)
  await shot(page, `${prefix}-login-dark.png`, 'Login page (dark)', prefix, 'dark')

  // Log in
  await login(page)
  await setDarkTheme(page)

  // Dashboard dark
  await page.goto(`${BASE}/`, { waitUntil: 'domcontentloaded' })
  await setDarkTheme(page)
  await shot(page, `${prefix}-dashboard-dark.png`, 'Dashboard (dark)', prefix, 'dark')

  // Spaces list dark
  await page.goto(`${BASE}/spaces`, { waitUntil: 'domcontentloaded' })
  await setDarkTheme(page)
  await shot(page, `${prefix}-spaces-list-dark.png`, 'Spaces list (dark)', prefix, 'dark')

  // Space view dark
  await page.goto(`${BASE}/spaces/${SPACE_KEY}`, { waitUntil: 'domcontentloaded' })
  await setDarkTheme(page)
  await shot(page, `${prefix}-space-view-dark.png`, 'Space view (dark)', prefix, 'dark')

  // Page view dark
  const slug = await findPageSlug(page)
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${slug}`, { waitUntil: 'domcontentloaded' })
  await setDarkTheme(page)
  await shot(page, `${prefix}-page-view-dark.png`, 'Page view (dark)', prefix, 'dark')

  // Editor dark
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${slug}/edit`, { waitUntil: 'domcontentloaded' })
  await settle(page)
  await page.waitForSelector(editorSel, { timeout: 10000 }).catch(() => {})
  await sleep(500)
  await setDarkTheme(page)
  await shot(page, `${prefix}-editor-dark.png`, 'Editor (dark)', prefix, 'dark')

  // Search dark
  await page.goto(`${BASE}/search`, { waitUntil: 'domcontentloaded' })
  await settle(page)
  await setDarkTheme(page)
  const searchInput = page.locator('input[type="search"], input[name="q"], input[placeholder*="earch"]').first()
  if (await searchInput.count() > 0) {
    await searchInput.fill('setup')
    await page.keyboard.press('Enter')
  }
  await settle(page)
  await shot(page, `${prefix}-search-dark.png`, 'Search results (dark)', prefix, 'dark')

  // Space settings dark
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/settings`, { waitUntil: 'domcontentloaded' })
  await setDarkTheme(page)
  await shot(page, `${prefix}-space-settings-dark.png`, 'Space settings (dark)', prefix, 'dark')

  await ctx.close()
}

// ─── Generate index.md ──────────────────────────────────────────────

function generateIndex(): void {
  const lines: string[] = [
    `# Altassian Visual Review — ${TODAY}`,
    '',
    'Full-page screenshots captured with Playwright against local dev.',
    '',
    '## Coverage Checklist',
    '',
  ]

  // Group by viewport
  for (const vp of VIEWPORTS) {
    const vpShots = manifest.filter(r => r.viewport === vp.label)
    const lightShots = vpShots.filter(r => r.theme === 'light')
    const darkShots = vpShots.filter(r => r.theme === 'dark')

    lines.push(`### ${vp.width}px ${vp.isMobile ? '(mobile)' : vp.width === 768 ? '(tablet)' : '(desktop)'}`)
    lines.push('')

    if (lightShots.length > 0) {
      lines.push('**Light mode:**')
      lines.push('')
      for (const s of lightShots) {
        const check = s.captured ? 'x' : ' '
        const note = s.note ? ` — ⚠ ${s.note}` : ''
        lines.push(`- [${check}] \`${s.file}\` — ${s.description}${note}`)
      }
      lines.push('')
    }

    if (darkShots.length > 0) {
      lines.push('**Dark mode:**')
      lines.push('')
      for (const s of darkShots) {
        const check = s.captured ? 'x' : ' '
        const note = s.note ? ` — ⚠ ${s.note}` : ''
        lines.push(`- [${check}] \`${s.file}\` — ${s.description}${note}`)
      }
      lines.push('')
    }
  }

  // Summary
  const captured = manifest.filter(r => r.captured).length
  const failed = manifest.filter(r => !r.captured).length

  lines.push('## Summary')
  lines.push('')
  lines.push(`- **Total screenshots:** ${manifest.length}`)
  lines.push(`- **Captured:** ${captured}`)
  if (failed > 0) lines.push(`- **Failed/Skipped:** ${failed}`)
  lines.push('')
  lines.push('## Routes Covered')
  lines.push('')
  lines.push('| Route | States |')
  lines.push('|-------|--------|')
  lines.push('| `/login` | default, dark |')
  lines.push('| `/register` | default |')
  lines.push('| `/landing` | default |')
  lines.push('| `/` (dashboard) | default, dark |')
  lines.push('| `/spaces` | list, dark |')
  lines.push('| `/spaces/create` | form |')
  lines.push('| `/spaces/:key` | page tree, dark, sidebar collapsed |')
  lines.push('| `/spaces/:key/pages/:slug` | view, dark |')
  lines.push('| `/spaces/:key/pages/:slug/edit` | content, floating toolbar, slash menu, dark |')
  lines.push('| `/spaces/:key/pages/new` | empty editor |')
  lines.push('| `/spaces/:key/pages/:slug/history` | version list |')
  lines.push('| `/search` | empty, with results, dark |')
  lines.push('| `/spaces/:key/settings` | default, dark |')
  lines.push('| `/*` (404) | not-found |')
  lines.push('')
  lines.push('## Breakpoints')
  lines.push('')
  lines.push('- **390px** — iPhone 14 / small mobile')
  lines.push('- **768px** — iPad / tablet portrait')
  lines.push('- **1280px** — Standard laptop / desktop')
  lines.push('')
  lines.push('## Visual Notes')
  lines.push('')
  lines.push('- Dark mode toggled via `localStorage` + `data-theme` + `.dark` class')
  lines.push('- Slash menu triggered by typing `/` in the editor')
  lines.push('- Floating toolbar appears on text selection (Ctrl+A)')
  lines.push('- Sidebar collapse captured where toggle button is available')
  lines.push('')
  lines.push('## Gaps / Not Captured')
  lines.push('')
  lines.push('- Password reset (route not implemented)')
  lines.push('- Loading skeletons (transient, hard to capture reliably)')
  lines.push('- Toast notifications (transient, appear on user actions)')
  lines.push('- Profile/account settings (route not yet present)')
  lines.push('- Attachment upload flow (requires file interaction)')
  lines.push('')
  lines.push('---')
  lines.push(`*Generated ${TODAY} by Playwright headless Chromium*`)
  lines.push('')

  fs.writeFileSync(path.join(OUT_DIR, 'index.md'), lines.join('\n'))
  console.log(`\n✓ index.md written`)
}

// ─── Main ───────────────────────────────────────────────────────────

async function main(): Promise<void> {
  // Ensure output dir
  fs.mkdirSync(OUT_DIR, { recursive: true })
  console.log(`Screenshots → ${OUT_DIR}\n`)

  const browser = await chromium.launch({ headless: true })

  try {
    // Capture all viewports in light mode
    for (const vp of VIEWPORTS) {
      await captureLightAtViewport(browser, vp)
    }

    // Capture dark mode at all viewports
    for (const vp of VIEWPORTS) {
      await captureDarkAtViewport(browser, vp)
    }
  } finally {
    await browser.close()
  }

  generateIndex()

  const captured = manifest.filter(r => r.captured).length
  console.log(`\nDone! ${captured}/${manifest.length} screenshots saved to ${OUT_DIR}`)
}

main().catch((err) => {
  console.error('Screenshot capture failed:', err)
  process.exit(1)
})

/**
 * Playwright screenshot capture for Altassian app.
 *
 * Prerequisites:
 *   - Backend running on http://localhost:8001
 *   - Frontend running on http://localhost:5173
 *   - Demo data seeded (python manage.py seed)
 *
 * Usage:
 *   npm run shots
 *
 * Output:
 *   artifacts/screenshots/YYYY-MM-DD/{01-login-desktop.png, ...}
 *   artifacts/screenshots/YYYY-MM-DD/index.md
 */

import { chromium, type Page, type Browser, type BrowserContext } from '@playwright/test'
import path from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const BASE = process.env.BASE_URL || 'http://localhost:5173'
const ROOT = path.resolve(__dirname, '..')
const TODAY = new Date().toISOString().slice(0, 10)
const OUT_DIR = path.join(ROOT, 'artifacts', 'screenshots', TODAY)

const CREDS = {
  username: process.env.SHOT_USER || 'admin',
  password: process.env.SHOT_PASS || 'AdminPass123',
}

const SPACE_KEY = 'ENG'
const PAGE_SLUG = 'architecture-overview'

const DESKTOP = { width: 1440, height: 900 }
const MOBILE = { width: 390, height: 844 }

interface ShotRecord {
  file: string
  description: string
  viewport: 'desktop' | 'mobile'
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

async function shot(page: Page, name: string, description: string, viewport: 'desktop' | 'mobile'): Promise<void> {
  await settle(page)
  const filePath = path.join(OUT_DIR, name)
  await page.screenshot({ path: filePath, fullPage: true })
  manifest.push({ file: name, description, viewport })
  console.log(`  ✓ ${name}`)
}

async function setDarkTheme(page: Page): Promise<void> {
  await page.evaluate(() => {
    localStorage.setItem('altassian-theme', 'dark')
    document.documentElement.setAttribute('data-theme', 'dark')
    document.documentElement.classList.add('dark')
  })
  await sleep(400)
}

async function login(page: Page): Promise<void> {
  await page.goto(`${BASE}/login`)
  await settle(page)
  await page.fill('input[type="text"], input[name="username"]', CREDS.username)
  await page.fill('input[type="password"]', CREDS.password)
  await page.click('button[type="submit"]')
  await page.waitForURL('**/', { timeout: 15000 })
  await settle(page)
}

const editorSel = '.tiptap, .ProseMirror, [contenteditable="true"]'

// ── Desktop captures (light) ──────────────────────────────────────

async function captureDesktop(browser: Browser): Promise<void> {
  console.log('\n=== DESKTOP (1440×900, light) ===\n')
  const ctx = await browser.newContext({ viewport: DESKTOP, colorScheme: 'light' })
  const page = await ctx.newPage()

  // Login page (before auth)
  await page.goto(`${BASE}/login`)
  await shot(page, '01-login-desktop.png', 'Login page', 'desktop')

  // Register page
  await page.goto(`${BASE}/register`)
  await shot(page, '02-register-desktop.png', 'Registration page', 'desktop')

  // Log in
  console.log('  Logging in…')
  await login(page)

  // Dashboard
  await page.goto(`${BASE}/`)
  await shot(page, '03-dashboard-desktop.png', 'Dashboard / home', 'desktop')

  // Spaces list
  await page.goto(`${BASE}/spaces`)
  await shot(page, '04-spaces-list-desktop.png', 'Spaces list', 'desktop')

  // Space view with page tree
  await page.goto(`${BASE}/spaces/${SPACE_KEY}`)
  await shot(page, '05-space-view-desktop.png', 'Space view with page tree', 'desktop')

  // Page view (doc with content)
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}`)
  await shot(page, '06-page-view-desktop.png', 'Page content view', 'desktop')

  // Editor (doc with content)
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}/edit`)
  await settle(page)
  await page.waitForSelector(editorSel, { timeout: 10000 }).catch(() => {})
  await sleep(500)
  await shot(page, '07-editor-desktop.png', 'Rich-text editor with content', 'desktop')

  // Editor – new empty doc
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/new`)
  await settle(page)
  await page.waitForSelector(editorSel, { timeout: 10000 }).catch(() => {})
  await sleep(500)
  await shot(page, '08-editor-empty-desktop.png', 'Editor (empty new page)', 'desktop')

  // Page history
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}/history`)
  await shot(page, '09-history-desktop.png', 'Page version history', 'desktop')

  // Search – empty
  await page.goto(`${BASE}/search`)
  await settle(page)
  await shot(page, '10-search-empty-desktop.png', 'Search page (empty)', 'desktop')

  // Search – with results
  const searchInput = page.locator('input[type="search"], input[name="q"], input[placeholder*="earch"]').first()
  if (await searchInput.count() > 0) {
    await searchInput.fill('architecture')
    await page.keyboard.press('Enter')
  }
  await settle(page)
  await shot(page, '11-search-results-desktop.png', 'Search results', 'desktop')

  // Space settings
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/settings`)
  await shot(page, '12-space-settings-desktop.png', 'Space settings', 'desktop')

  // 404 page
  await page.goto(`${BASE}/this-does-not-exist-404`)
  await shot(page, '13-404-desktop.png', '404 not-found page', 'desktop')

  await ctx.close()
}

// ── Dark mode (desktop) ───────────────────────────────────────────

async function captureDark(browser: Browser): Promise<void> {
  console.log('\n=== DARK MODE (1440×900) ===\n')
  const ctx = await browser.newContext({ viewport: DESKTOP, colorScheme: 'dark' })
  const page = await ctx.newPage()

  await page.goto(`${BASE}/login`)
  await setDarkTheme(page)
  await shot(page, '14-login-dark-desktop.png', 'Login page (dark)', 'desktop')

  await login(page)
  await setDarkTheme(page)

  await page.goto(`${BASE}/`)
  await setDarkTheme(page)
  await shot(page, '15-dashboard-dark-desktop.png', 'Dashboard (dark)', 'desktop')

  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}`)
  await setDarkTheme(page)
  await shot(page, '16-page-view-dark-desktop.png', 'Page view (dark)', 'desktop')

  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}/edit`)
  await settle(page)
  await page.waitForSelector(editorSel, { timeout: 10000 }).catch(() => {})
  await sleep(500)
  await setDarkTheme(page)
  await shot(page, '17-editor-dark-desktop.png', 'Editor (dark)', 'desktop')

  await page.goto(`${BASE}/search`)
  await settle(page)
  await setDarkTheme(page)
  const searchInput = page.locator('input[type="search"], input[name="q"], input[placeholder*="earch"]').first()
  if (await searchInput.count() > 0) {
    await searchInput.fill('architecture')
    await page.keyboard.press('Enter')
  }
  await settle(page)
  await shot(page, '18-search-dark-desktop.png', 'Search results (dark)', 'desktop')

  await ctx.close()
}

// ── Mobile captures ───────────────────────────────────────────────

async function captureMobile(browser: Browser): Promise<void> {
  console.log('\n=== MOBILE (390×844) ===\n')
  const ctx = await browser.newContext({
    viewport: MOBILE,
    colorScheme: 'light',
    isMobile: true,
    hasTouch: true,
  })
  const page = await ctx.newPage()

  await page.goto(`${BASE}/login`)
  await shot(page, '01-login-mobile.png', 'Login page (mobile)', 'mobile')

  await login(page)

  await page.goto(`${BASE}/`)
  await shot(page, '02-dashboard-mobile.png', 'Dashboard (mobile)', 'mobile')

  await page.goto(`${BASE}/spaces`)
  await shot(page, '03-spaces-list-mobile.png', 'Spaces list (mobile)', 'mobile')

  await page.goto(`${BASE}/spaces/${SPACE_KEY}`)
  await shot(page, '04-space-view-mobile.png', 'Space view (mobile)', 'mobile')

  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}`)
  await shot(page, '05-page-view-mobile.png', 'Page view (mobile)', 'mobile')

  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${PAGE_SLUG}/edit`)
  await settle(page)
  await sleep(500)
  await shot(page, '06-editor-mobile.png', 'Editor (mobile)', 'mobile')

  await page.goto(`${BASE}/search`)
  await settle(page)
  const searchInput = page.locator('input[type="search"], input[name="q"], input[placeholder*="earch"]').first()
  if (await searchInput.count() > 0) {
    await searchInput.fill('architecture')
    await page.keyboard.press('Enter')
  }
  await settle(page)
  await shot(page, '07-search-mobile.png', 'Search results (mobile)', 'mobile')

  await page.goto(`${BASE}/this-does-not-exist-404`)
  await shot(page, '08-404-mobile.png', '404 page (mobile)', 'mobile')

  await ctx.close()
}

// ── Generate index.md ─────────────────────────────────────────────

function generateIndex(): void {
  const desktopShots = manifest.filter(r => r.viewport === 'desktop')
  const mobileShots = manifest.filter(r => r.viewport === 'mobile')

  const lines: string[] = [
    `# Altassian Screenshots — ${TODAY}`,
    '',
    `Captured on ${TODAY} using Playwright against local dev servers.`,
    '',
    '## Desktop (1440×900)',
    '',
  ]

  for (const s of desktopShots) {
    lines.push(`### ${s.description}`)
    lines.push(`![${s.description}](./${s.file})`)
    lines.push('')
  }

  lines.push('## Mobile (390×844)')
  lines.push('')

  for (const s of mobileShots) {
    lines.push(`### ${s.description}`)
    lines.push(`![${s.description}](./${s.file})`)
    lines.push('')
  }

  lines.push('---')
  lines.push(`*${manifest.length} screenshots total*`)
  lines.push('')

  fs.writeFileSync(path.join(OUT_DIR, 'index.md'), lines.join('\n'))
  console.log(`\n✓ index.md written`)
}

// ── Main ──────────────────────────────────────────────────────────

async function main(): Promise<void> {
  // Clean + create output dir (idempotent)
  if (fs.existsSync(OUT_DIR)) {
    fs.rmSync(OUT_DIR, { recursive: true })
  }
  fs.mkdirSync(OUT_DIR, { recursive: true })
  console.log(`Screenshots → ${OUT_DIR}\n`)

  const browser = await chromium.launch({ headless: true })

  try {
    await captureDesktop(browser)
    await captureDark(browser)
    await captureMobile(browser)
  } finally {
    await browser.close()
  }

  generateIndex()

  console.log(`\nDone! ${manifest.length} screenshots saved to ${OUT_DIR}`)
}

main().catch((err) => {
  console.error('Screenshot capture failed:', err)
  process.exit(1)
})

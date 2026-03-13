/**
 * Final Screenshot Capture — Product overview screenshots.
 *
 * Output: ~/.openclaw/workspace/altassian_screenshots/2026-03-13/
 * Viewport: 1440x900 (desktop)
 * Themes: light, dark
 *
 * Prerequisites:
 *   - Backend running on http://localhost:8001
 *   - Frontend running on http://localhost:5173
 *   - Admin user exists (admin / AdminPass123)
 */

import { chromium, type Page, type BrowserContext } from '@playwright/test'
import path from 'path'
import fs from 'fs'
import os from 'os'

const BASE = process.env.BASE_URL || 'http://localhost:5173'
const DATE = '2026-03-13'
const OUT = path.join(os.homedir(), '.openclaw', 'workspace', 'altassian_screenshots', DATE)

const CREDS = { username: 'admin', password: 'AdminPass123' }
const SPACE_KEY = 'ENG'
const PAGE_SLUG = 'architecture-overview'
const ALT_PAGE_SLUG = 'development-setup'

const WIDTH = 1440
const HEIGHT = 900

type Theme = 'light' | 'dark'

interface ShotEntry {
  num: string
  name: string
  theme: Theme
  file: string
  ok: boolean
}

const results: ShotEntry[] = []

function sleep(ms: number): Promise<void> {
  return new Promise(r => setTimeout(r, ms))
}

async function settle(page: Page): Promise<void> {
  await page.waitForLoadState('domcontentloaded').catch(() => {})
  await page.waitForFunction(() => (window as any).__APP_READY__ === true, { timeout: 12000 }).catch(() => {})
  await page.waitForLoadState('networkidle').catch(() => {})
  await sleep(800)
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

async function snap(
  page: Page,
  num: string,
  name: string,
  theme: Theme,
): Promise<void> {
  await settle(page)
  const filename = `${num}-${name}-${theme}.png`
  const filePath = path.join(OUT, filename)
  try {
    await page.screenshot({ path: filePath, fullPage: true })
    results.push({ num, name, theme, file: filename, ok: true })
    console.log(`  ✓ ${filename}`)
  } catch (e: any) {
    results.push({ num, name, theme, file: filename, ok: false })
    console.log(`  ✗ ${filename} — ${e.message?.slice(0, 80)}`)
  }
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

const editorSel = '.tiptap, .ProseMirror, [contenteditable="true"]'

async function captureTheme(ctx: BrowserContext, theme: Theme): Promise<void> {
  console.log(`\n=== ${theme.toUpperCase()} MODE (1440×900) ===\n`)
  const page = await ctx.newPage()

  const applyTheme = async () => setTheme(page, theme)

  // 01 — Landing
  await page.goto(`${BASE}/landing`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await snap(page, '01', 'landing', theme)

  // 02 — Login
  await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await snap(page, '02', 'login', theme)

  // 03 — Register / Signup
  await page.goto(`${BASE}/register`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await snap(page, '03', 'signup', theme)

  // Log in
  console.log('  Logging in...')
  await login(page)
  await applyTheme()

  // 04 — Dashboard
  await page.goto(`${BASE}/`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await snap(page, '04', 'dashboard', theme)

  // 05 — Spaces list (projects)
  await page.goto(`${BASE}/spaces`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await snap(page, '05', 'projects', theme)

  // 06 — Space detail (project/:id)
  await page.goto(`${BASE}/spaces/${SPACE_KEY}`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await snap(page, '06', 'project-detail', theme)

  // 07 — Create space
  await page.goto(`${BASE}/spaces/create`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await snap(page, '07', 'create-space', theme)

  // Find a valid page slug
  const slug = await findPageSlug(page)
  console.log(`  Using page slug: ${slug}`)

  // 08 — Page view
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${slug}`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await snap(page, '08', 'page-view', theme)

  // 09 — Editor (TipTap)
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${slug}/edit`, { waitUntil: 'domcontentloaded' })
  await settle(page)
  await page.waitForSelector(editorSel, { timeout: 10000 }).catch(() => {})
  await sleep(500)
  await applyTheme()
  await snap(page, '09', 'editor', theme)

  // 10 — Editor bubble menu (select text)
  const editorEl = page.locator(editorSel).first()
  if (await editorEl.count() > 0) {
    await editorEl.click()
    await sleep(200)
    await page.keyboard.press('Control+a')
    await sleep(800)
    await snap(page, '10', 'editor-toolbar', theme)
  }

  // 11 — Editor slash menu
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
  await snap(page, '11', 'editor-slash-menu', theme)

  // 12 — Page history
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/pages/${slug}/history`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await snap(page, '12', 'page-history', theme)

  // 13 — Search
  await page.goto(`${BASE}/search`, { waitUntil: 'domcontentloaded' })
  await settle(page)
  await applyTheme()
  const searchInput = page.locator('input[type="search"], input[name="q"], input[placeholder*="earch"]').first()
  if (await searchInput.count() > 0) {
    await searchInput.fill('architecture')
    await page.keyboard.press('Enter')
  }
  await settle(page)
  await snap(page, '13', 'search-results', theme)

  // 14 — Space settings
  await page.goto(`${BASE}/spaces/${SPACE_KEY}/settings`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await snap(page, '14', 'settings', theme)

  // 15 — 404 page
  await page.goto(`${BASE}/this-page-does-not-exist-404`, { waitUntil: 'domcontentloaded' })
  await applyTheme()
  await snap(page, '15', '404', theme)

  await page.close()
}

async function main(): Promise<void> {
  // Clean + create output dir
  if (fs.existsSync(OUT)) {
    fs.rmSync(OUT, { recursive: true })
  }
  fs.mkdirSync(OUT, { recursive: true })

  console.log(`Screenshots → ${OUT}\n`)

  const browser = await chromium.launch({ headless: true })

  try {
    // Light mode
    const lightCtx = await browser.newContext({
      viewport: { width: WIDTH, height: HEIGHT },
      colorScheme: 'light',
    })
    await captureTheme(lightCtx, 'light')
    await lightCtx.close()

    // Dark mode
    const darkCtx = await browser.newContext({
      viewport: { width: WIDTH, height: HEIGHT },
      colorScheme: 'dark',
    })
    await captureTheme(darkCtx, 'dark')
    await darkCtx.close()
  } finally {
    await browser.close()
  }

  // Write README
  const captured = results.filter(r => r.ok).length
  const readme = [
    `# Altassian Product Screenshots — ${DATE}`,
    '',
    `${captured} screenshots captured at 1440×900 in both light and dark mode.`,
    '',
    '## Files',
    '',
    '| # | Page | Light | Dark |',
    '|---|------|-------|------|',
  ]

  const nums = [...new Set(results.map(r => r.num))]
  for (const num of nums) {
    const shots = results.filter(r => r.num === num)
    const name = shots[0]?.name || ''
    const lightFile = shots.find(r => r.theme === 'light')
    const darkFile = shots.find(r => r.theme === 'dark')
    const lightMark = lightFile?.ok ? `![](${lightFile.file})` : '—'
    const darkMark = darkFile?.ok ? `![](${darkFile.file})` : '—'
    readme.push(`| ${num} | ${name} | ${lightMark} | ${darkMark} |`)
  }

  readme.push('')
  readme.push('## How to Regenerate')
  readme.push('')
  readme.push('```bash')
  readme.push('# 1. Start backend')
  readme.push('cd ~/.openclaw/workspace/altassian_backend')
  readme.push('source venv/bin/activate')
  readme.push('python manage.py runserver 0.0.0.0:8001')
  readme.push('')
  readme.push('# 2. Start frontend')
  readme.push('cd ~/.openclaw/workspace/altassian_frontend')
  readme.push('npm run dev')
  readme.push('')
  readme.push('# 3. Capture screenshots')
  readme.push('npx tsx scripts/capture-final-screenshots.ts')
  readme.push('```')
  readme.push('')
  readme.push('## Environment')
  readme.push('')
  readme.push('- Backend: `http://localhost:8001` (Django + DRF)')
  readme.push('- Frontend: `http://localhost:5173` (Vite + React)')
  readme.push('- Credentials: See `.env.local` (do not commit real credentials)')
  readme.push('- Viewport: 1440×900')
  readme.push('- Playwright headless Chromium')
  readme.push('')

  fs.writeFileSync(path.join(OUT, 'README.md'), readme.join('\n'))
  console.log(`\n✓ README.md written`)
  console.log(`Done! ${captured}/${results.length} screenshots saved to ${OUT}`)
}

main().catch((err) => {
  console.error('Screenshot capture failed:', err)
  process.exit(1)
})

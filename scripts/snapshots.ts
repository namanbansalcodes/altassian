/**
 * Playwright screenshot pipeline for Altassian frontend.
 *
 * Captures every major page at desktop (1440×900) and mobile (390×844),
 * in both light and dark themes.
 *
 * Output:  docs/screenshots/<viewport>/<route>.png
 *          docs/screenshots/manifest.json
 *          docs/screenshots/index.md
 *
 * Env:
 *   ALTASSIAN_FRONTEND_URL  — default http://localhost:5173
 *   ALTASSIAN_BACKEND_URL   — default http://localhost:8001
 *   ALTASSIAN_DEMO_EMAIL    — default "admin"
 *   ALTASSIAN_DEMO_PASSWORD — default "AdminPass123"
 *
 * Usage:
 *   pnpm snapshots          # or npm run snapshots
 */

import { chromium, type Page, type Browser } from '@playwright/test'
import path from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// ── Config ────────────────────────────────────────────────────────

const BASE_URL = process.env.ALTASSIAN_FRONTEND_URL || 'http://localhost:5173'
const CREDS = {
  username: process.env.ALTASSIAN_DEMO_EMAIL || 'admin',
  password: process.env.ALTASSIAN_DEMO_PASSWORD || 'AdminPass123',
}

const ROOT = path.resolve(__dirname, '..')
const OUT_DIR = path.join(ROOT, 'docs', 'screenshots')

const SPACE_KEY = 'ENG'
const PREFERRED_SLUGS = ['architecture-overview', 'development-setup']

interface Viewport {
  label: string
  width: number
  height: number
  isMobile: boolean
}

const VIEWPORTS: Viewport[] = [
  { label: 'desktop', width: 1440, height: 900, isMobile: false },
  { label: 'mobile', width: 390, height: 844, isMobile: true },
]

type Theme = 'light' | 'dark'

interface ManifestEntry {
  route: string
  file: string
  viewport: string
  theme: Theme
  description: string
}

const manifest: ManifestEntry[] = []

// ── Helpers ───────────────────────────────────────────────────────

function sleep(ms: number): Promise<void> {
  return new Promise(r => setTimeout(r, ms))
}

async function settle(page: Page): Promise<void> {
  await page.waitForLoadState('domcontentloaded').catch(() => {})
  await page.waitForFunction(
    () => (window as any).__APP_READY__ === true,
    { timeout: 10_000 },
  ).catch(() => {})
  await page.waitForLoadState('networkidle').catch(() => {})
  await sleep(800)
}

/** Inject CSS to suppress animations & transitions for deterministic screenshots. */
async function reduceMotion(page: Page): Promise<void> {
  await page.addStyleTag({
    content: `*, *::before, *::after {
      animation-duration: 0s !important;
      animation-delay: 0s !important;
      transition-duration: 0s !important;
      transition-delay: 0s !important;
    }`,
  })
}

function sanitize(route: string): string {
  return route
    .replace(/^\//, '')
    .replace(/\//g, '-')
    .replace(/[^a-zA-Z0-9_-]/g, '_') || 'home'
}

async function snap(
  page: Page,
  route: string,
  description: string,
  vpLabel: string,
  theme: Theme,
  suffix?: string,
): Promise<void> {
  await settle(page)
  const name = `${sanitize(route)}${suffix ? `-${suffix}` : ''}-${theme}.png`
  const dir = path.join(OUT_DIR, vpLabel)
  fs.mkdirSync(dir, { recursive: true })
  const filePath = path.join(dir, name)
  try {
    await page.screenshot({ path: filePath, fullPage: true })
    manifest.push({
      route,
      file: `${vpLabel}/${name}`,
      viewport: vpLabel,
      theme,
      description,
    })
    console.log(`  ✓ ${vpLabel}/${name}`)
  } catch (e: any) {
    console.log(`  ✗ ${vpLabel}/${name} — ${e.message?.slice(0, 80)}`)
  }
}

// ── Theme toggling ────────────────────────────────────────────────

async function setTheme(page: Page, theme: Theme): Promise<void> {
  await page.evaluate((t: string) => {
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

// ── Auth ──────────────────────────────────────────────────────────

async function login(page: Page): Promise<void> {
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' })
  await settle(page)
  await page.fill('input[type="text"], input[name="username"]', CREDS.username)
  await page.fill('input[type="password"]', CREDS.password)
  await page.click('button[type="submit"]')
  await page.waitForURL('**/', { timeout: 15_000 }).catch(() => {})
  await settle(page)
}

// ── Find a valid page slug ────────────────────────────────────────

async function findPageSlug(page: Page): Promise<string> {
  for (const slug of PREFERRED_SLUGS) {
    await page.goto(`${BASE_URL}/spaces/${SPACE_KEY}/pages/${slug}`, {
      waitUntil: 'domcontentloaded',
    })
    await sleep(1500)
    const body = await page.textContent('body').catch(() => '')
    if (body && !body.includes('Not Found') && !body.includes('404') && body.length > 200) {
      return slug
    }
  }
  // Fallback: grab first page link from space view
  await page.goto(`${BASE_URL}/spaces/${SPACE_KEY}`, { waitUntil: 'domcontentloaded' })
  await settle(page)
  const href = await page
    .locator(`a[href*="/spaces/${SPACE_KEY}/pages/"]`)
    .first()
    .getAttribute('href')
    .catch(() => null)
  if (href) {
    const m = href.match(/\/pages\/([^/]+)/)
    if (m) return m[1]
  }
  return PREFERRED_SLUGS[0]
}

// ── Route definitions ─────────────────────────────────────────────

const EDITOR_SEL = '.tiptap, .ProseMirror, [contenteditable="true"]'

interface RouteCapture {
  route: string
  description: string
  /** If true, requires authentication */
  auth: boolean
  /** Extra steps after navigation */
  after?: (page: Page) => Promise<void>
  suffix?: string
}

function buildRoutes(slug: string): RouteCapture[] {
  return [
    // ── Public pages ──
    { route: '/login', description: 'Login page', auth: false },
    { route: '/register', description: 'Registration page', auth: false },
    { route: '/landing', description: 'Landing page', auth: false },

    // ── Authenticated pages ──
    { route: '/', description: 'Dashboard / Home', auth: true },
    { route: '/spaces', description: 'Spaces list', auth: true },
    { route: '/spaces/create', description: 'Create space form', auth: true },
    { route: `/spaces/${SPACE_KEY}`, description: 'Space view with page tree', auth: true },
    {
      route: `/spaces/${SPACE_KEY}/pages/${slug}`,
      description: 'Page content view',
      auth: true,
    },
    {
      route: `/spaces/${SPACE_KEY}/pages/${slug}/edit`,
      description: 'Rich-text editor with content',
      auth: true,
      after: async (page: Page) => {
        await page.waitForSelector(EDITOR_SEL, { timeout: 10_000 }).catch(() => {})
        await sleep(600)
      },
    },
    {
      route: `/spaces/${SPACE_KEY}/pages/${slug}/edit`,
      description: 'Editor — slash command menu',
      auth: true,
      suffix: 'slash-menu',
      after: async (page: Page) => {
        await page.waitForSelector(EDITOR_SEL, { timeout: 10_000 }).catch(() => {})
        await sleep(400)
        const editor = page.locator(EDITOR_SEL).first()
        if ((await editor.count()) > 0) {
          await editor.click()
          await page.keyboard.press('End')
          await page.keyboard.press('Enter')
          await page.keyboard.type('/')
          await sleep(1000)
        }
      },
    },
    {
      route: `/spaces/${SPACE_KEY}/pages/new`,
      description: 'Editor (empty new page)',
      auth: true,
      after: async (page: Page) => {
        await page.waitForSelector(EDITOR_SEL, { timeout: 10_000 }).catch(() => {})
        await sleep(400)
      },
    },
    {
      route: `/spaces/${SPACE_KEY}/pages/${slug}/history`,
      description: 'Page version history',
      auth: true,
    },
    {
      route: '/search',
      description: 'Search page (empty)',
      auth: true,
    },
    {
      route: '/search',
      description: 'Search with results',
      auth: true,
      suffix: 'results',
      after: async (page: Page) => {
        const input = page
          .locator('input[type="search"], input[name="q"], input[placeholder*="earch"]')
          .first()
        if ((await input.count()) > 0) {
          await input.fill('architecture')
          await page.keyboard.press('Enter')
        }
        await settle(page)
      },
    },
    {
      route: `/spaces/${SPACE_KEY}/settings`,
      description: 'Space settings',
      auth: true,
    },
    { route: '/nonexistent-route-404', description: '404 not-found page', auth: true },
  ]
}

// ── Capture loop ──────────────────────────────────────────────────

async function captureViewport(
  browser: Browser,
  vp: Viewport,
  theme: Theme,
  routes: RouteCapture[],
): Promise<void> {
  console.log(`\n=== ${vp.label} ${vp.width}×${vp.height} — ${theme.toUpperCase()} ===\n`)

  const ctx = await browser.newContext({
    viewport: { width: vp.width, height: vp.height },
    colorScheme: theme,
    isMobile: vp.isMobile,
    hasTouch: vp.isMobile,
  })
  const page = await ctx.newPage()
  await reduceMotion(page)

  let loggedIn = false

  for (const r of routes) {
    if (r.auth && !loggedIn) {
      console.log('  Logging in…')
      await login(page)
      await setTheme(page, theme)
      loggedIn = true
    }

    await page.goto(`${BASE_URL}${r.route}`, { waitUntil: 'domcontentloaded' })
    if (loggedIn) await setTheme(page, theme)
    if (r.after) await r.after(page)

    await snap(page, r.route, r.description, vp.label, theme, r.suffix)
  }

  await ctx.close()
}

// ── Output generators ─────────────────────────────────────────────

function writeManifest(): void {
  const grouped: Record<string, string[]> = {}
  for (const e of manifest) {
    if (!grouped[e.route]) grouped[e.route] = []
    grouped[e.route].push(e.file)
  }
  const out = { generatedAt: new Date().toISOString(), routes: grouped, entries: manifest }
  fs.writeFileSync(path.join(OUT_DIR, 'manifest.json'), JSON.stringify(out, null, 2))
  console.log('\n✓ manifest.json written')
}

function writeIndex(): void {
  const lines: string[] = [
    '# Altassian Screenshots',
    '',
    `> Auto-generated by \`scripts/snapshots.ts\` on ${new Date().toISOString().slice(0, 10)}.`,
    '',
  ]

  for (const vp of VIEWPORTS) {
    for (const theme of ['light', 'dark'] as Theme[]) {
      const shots = manifest.filter(e => e.viewport === vp.label && e.theme === theme)
      if (shots.length === 0) continue
      lines.push(`## ${vp.label} — ${theme}`)
      lines.push('')
      for (const s of shots) {
        lines.push(`### ${s.description}`)
        lines.push(`![${s.description}](${s.file})`)
        lines.push('')
      }
    }
  }

  lines.push('---')
  lines.push(`*${manifest.length} screenshots total*`)
  lines.push('')

  fs.writeFileSync(path.join(OUT_DIR, 'index.md'), lines.join('\n'))
  console.log('✓ index.md written')
}

function writeReadme(): void {
  const readme = `# Screenshot Pipeline

Automated Playwright-based screenshot capture for the Altassian frontend.

## Quick Start

\`\`\`bash
# 1. Start backend + frontend
python manage.py runserver 0.0.0.0:8001   # backend
cd ./frontend && pnpm dev       # frontend on :5173

# 2. Run screenshots
pnpm snapshots   # or: npm run snapshots
\`\`\`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| \`ALTASSIAN_FRONTEND_URL\` | \`http://localhost:5173\` | Frontend base URL |
| \`ALTASSIAN_BACKEND_URL\` | \`http://localhost:8001\` | Backend base URL |
| \`ALTASSIAN_DEMO_EMAIL\` | \`admin\` | Login username/email |
| \`ALTASSIAN_DEMO_PASSWORD\` | \`AdminPass123\` | Login password |

## Output Structure

\`\`\`
docs/screenshots/
├── desktop/          # 1440×900
│   ├── home-light.png
│   ├── home-dark.png
│   └── ...
├── mobile/           # 390×844
│   ├── home-light.png
│   ├── home-dark.png
│   └── ...
├── manifest.json     # Route → file mapping
├── index.md          # Visual gallery with embedded images
└── README.md         # This file
\`\`\`

## Viewports

- **Desktop**: 1440×900 (standard laptop)
- **Mobile**: 390×844 (iPhone 12/13/14)

## Themes

Both **light** and **dark** are captured for every route.

## Routes Captured

| Route | States |
|-------|--------|
| \`/login\` | light, dark |
| \`/register\` | light, dark |
| \`/landing\` | light, dark |
| \`/\` (dashboard) | light, dark |
| \`/spaces\` | light, dark |
| \`/spaces/create\` | light, dark |
| \`/spaces/:key\` | light, dark |
| \`/spaces/:key/pages/:slug\` | light, dark |
| \`/spaces/:key/pages/:slug/edit\` | light, dark, slash-menu |
| \`/spaces/:key/pages/new\` | light, dark |
| \`/spaces/:key/pages/:slug/history\` | light, dark |
| \`/search\` | empty, with results (light, dark) |
| \`/spaces/:key/settings\` | light, dark |
| \`/*\` (404) | light, dark |

## CI Usage

Add to your CI pipeline:

\`\`\`yaml
- name: Screenshot capture
  run: |
    npx playwright install --with-deps chromium
    npm run snapshots
- uses: actions/upload-artifact@v4
  with:
    name: screenshots
    path: docs/screenshots/
\`\`\`

## Sending to Naman

Screenshots should be sent to Naman via Telegram (user ID: 7863363002).
After committing, share the GitHub links to the \`docs/screenshots/\` directory.
`

  fs.writeFileSync(path.join(OUT_DIR, 'README.md'), readme)
  console.log('✓ README.md written')
}

// ── Main ──────────────────────────────────────────────────────────

async function main(): Promise<void> {
  // Clean output
  if (fs.existsSync(OUT_DIR)) {
    // Preserve README.md by removing only generated content
    for (const sub of ['desktop', 'mobile']) {
      const d = path.join(OUT_DIR, sub)
      if (fs.existsSync(d)) fs.rmSync(d, { recursive: true })
    }
    for (const f of ['manifest.json', 'index.md']) {
      const p = path.join(OUT_DIR, f)
      if (fs.existsSync(p)) fs.unlinkSync(p)
    }
  }
  fs.mkdirSync(OUT_DIR, { recursive: true })
  console.log(`Screenshots → ${OUT_DIR}\n`)

  const browser = await chromium.launch({ headless: true })

  try {
    // Determine a valid page slug before capturing
    const probePage = await browser.newPage()
    await login(probePage)
    const slug = await findPageSlug(probePage)
    await probePage.close()
    console.log(`Using page slug: ${slug}\n`)

    const routes = buildRoutes(slug)

    for (const vp of VIEWPORTS) {
      for (const theme of ['light', 'dark'] as Theme[]) {
        await captureViewport(browser, vp, theme, routes)
      }
    }
  } finally {
    await browser.close()
  }

  writeManifest()
  writeIndex()
  writeReadme()

  console.log(`\nDone! ${manifest.length} screenshots saved to ${OUT_DIR}`)
  console.log(`\n📬 Screenshots should be sent to Naman via Telegram (user ID: 7863363002).`)
  console.log(`   Share GitHub links to: docs/screenshots/`)
}

main().catch((err) => {
  console.error('Screenshot capture failed:', err)
  process.exit(1)
})

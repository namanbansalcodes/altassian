import { test, expect } from '@playwright/test';

const BASE = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173';

test('login → spaces → page view flow', async ({ page }) => {
  page.on('console', (msg) => console.log('BROWSER:', msg.type(), msg.text()));

  await page.goto(BASE + '/login');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: 'test-results/login.png', fullPage: true });
  const html = await page.content();
  require('fs').writeFileSync('test-results/login.html', html);

  const userInput = page.getByPlaceholder('Username');
  await userInput.waitFor({ state: 'visible', timeout: 10000 });
  await userInput.fill('demo');
  await page.getByPlaceholder('Password').fill('demo123');
  await page.getByRole('button', { name: 'Login' }).click();

  await page.waitForURL(BASE + '/');
  await page.goto(BASE + '/spaces');
  await page.getByRole('button').first().click();
  await page.getByRole('button').first().click();

  await expect(page.getByRole('button', { name: 'Save' })).toBeVisible();
});

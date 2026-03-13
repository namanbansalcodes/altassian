import { test, expect } from '@playwright/test';

const BASE = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173';

test('login → spaces → page view flow', async ({ page }) => {
  await page.goto(BASE + '/login');
  await page.getByPlaceholder('Username').fill('demo');
  await page.getByPlaceholder('Password').fill('demo123');
  await page.getByRole('button', { name: 'Login' }).click();

  await page.waitForURL(BASE + '/');
  await page.goto(BASE + '/spaces');
  await page.getByRole('button').first().click();
  await page.getByRole('button').first().click();

  await expect(page.getByRole('button', { name: 'Save' })).toBeVisible();
});

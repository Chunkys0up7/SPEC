import { test, expect } from '@playwright/test';

test('hub loads with four room cards', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('GLADSTONE')).toBeVisible();
  await expect(page.getByText('LOCKDOWN')).toBeVisible();
  await expect(page.getByText('The Front Desk')).toBeVisible();
  await expect(page.getByText('The Records Room')).toBeVisible();
  await expect(page.getByText('The Billing Office')).toBeVisible();
  await expect(page.getByText('The Provider Suite')).toBeVisible();
});

test('entering a room shows the canvas and dock', async ({ page }) => {
  await page.goto('/');
  await page.getByText('The Front Desk').click();
  await expect(page.getByText('On the spot · turn 1')).toBeVisible();
  await expect(page.getByText('Clue inventory')).toBeVisible();
});

test('reset clears state', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Reset quest' }).click();
  await page.getByRole('button', { name: 'Yes, wipe everything' }).click();
  await expect(page.getByText('No points yet')).toBeVisible();
});

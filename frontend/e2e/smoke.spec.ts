import { test, expect } from '@playwright/test'

test('app loads for authenticated user', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('body')).toBeVisible()
})

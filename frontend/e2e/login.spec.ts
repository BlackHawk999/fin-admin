import { test, expect } from '@playwright/test'

const USER = process.env.E2E_USER ?? 'admin'
const PASS = process.env.E2E_PASS ?? 'admin123'

// ⚠️ если у тебя другой путь логина — поменяй тут
const LOGIN_URL = '/login'

test('login: success redirects to home', async ({ page }) => {
  await page.goto(LOGIN_URL)

  await page.getByTestId('login-username').locator('input').fill(USER)
  await page.getByTestId('login-password').locator('input').fill(PASS)
  await page.getByTestId('login-submit').click()

  await expect(page).toHaveURL(/\/$/)
})

test('login: wrong password shows inline error', async ({ page }) => {
  await page.goto(LOGIN_URL)

  await page.getByTestId('login-username').locator('input').fill(USER)
  await page.getByTestId('login-password').locator('input').fill('wrong-pass')
  await page.getByTestId('login-submit').click()

  await expect(page.getByTestId('login-error')).toBeVisible()
})

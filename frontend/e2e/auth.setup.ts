import { test as setup, expect } from '@playwright/test'

const USER = process.env.E2E_USER ?? 'admin'
const PASS = process.env.E2E_PASS ?? 'admin123'

setup('authenticate', async ({ page }) => {
  await page.goto('/')

  // если попали на логин — логинимся
  await expect(page.getByTestId('login-submit')).toBeVisible()

  await page.getByTestId('login-username').fill(USER)
  await page.getByTestId('login-password').fill(PASS)
  await page.getByTestId('login-submit').click()

  // дождаться перехода после логина
  await expect(page).toHaveURL(/\/$/)

  await page.context().storageState({ path: 'e2e/.auth.json' })
})

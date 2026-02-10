import { test, expect } from '@playwright/test'

test('authenticate', async ({ page }) => {
  const username = process.env.E2E_USERNAME
  const password = process.env.E2E_PASSWORD

  if (!username || !password) {
    throw new Error('Missing E2E_USERNAME or E2E_PASSWORD. Set them in GitHub Actions Secrets.')
  }

  await page.goto('/login')

  // ВАЖНО: у тебя на login пока нет data-testid, поэтому ищем по label
  await page.getByLabel('Логин').fill(username)
  await page.getByLabel('Пароль').fill(password)

  // кнопка submit
  await page.getByRole('button', { name: /Войти/i }).click()

  // если логин успешен — обычно редирект на "/"
  await expect(page).toHaveURL(/\/$/)

  // сохраняем storageState
  await page.context().storageState({ path: 'e2e/.auth.json' })
})

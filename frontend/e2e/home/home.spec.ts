import { test, expect } from '@playwright/test'

function uniq(prefix = 'E2E') {
  return `${prefix} ${Date.now()}`
}

async function waitModalVisible(page: any) {
  await page.waitForSelector('[data-testid="home-expense-modal"]', {
    state: 'visible',
    timeout: 5000,
  })
}

async function waitModalHidden(page: any) {
  await page.waitForSelector('[data-testid="home-expense-modal"]', {
    state: 'hidden',
    timeout: 5000,
  })
}

test('home: dashboard loads (summary, chart, last expenses)', async ({ page }) => {
  await page.goto('/')

  await expect(page.getByTestId('home-page')).toBeVisible()
  await expect(page.getByTestId('home-title')).toBeVisible()

  // summary может быть либо loading, либо готов
  await expect(
    page.locator('[data-testid="home-summary-loading"], [data-testid="home-summary"]'),
  ).toBeVisible()

  // chart секция
  await expect(page.getByTestId('home-chart-section')).toBeVisible()
  await expect(page.getByTestId('home-chart-toggles')).toBeVisible()

  // last expenses секция
  await expect(page.getByTestId('home-last-expenses-section')).toBeVisible()
})

test('home: chart range toggles 7 / 30 / 90 are clickable', async ({ page }) => {
  await page.goto('/')

  await expect(page.getByTestId('home-page')).toBeVisible()

  await page.getByTestId('home-chart-days-7').click()
  await page.getByTestId('home-chart-days-30').click()
  await page.getByTestId('home-chart-days-90').click()

  // важно лишь, что страница не сломалась
  await expect(page.getByTestId('home-chart-section')).toBeVisible()
})

test('home: add expense from home -> appears in last expenses table', async ({ page }) => {
  await page.goto('/')

  await page.getByTestId('home-add-expense').click()
  await waitModalVisible(page)

  const category = uniq('CatHome')
  const comment = uniq('E2E home') // comment в таблице НЕ показывается, но нужен для API

  await page.getByTestId('home-expense-amount').fill('11000')
  await page.getByTestId('home-expense-category').fill(category)
  await page.getByTestId('home-expense-comment').fill(comment)

  await page.getByTestId('home-expense-submit').click()
  await waitModalHidden(page)

  // В таблице Home отображается CATEGORY, а не comment
  await expect(page.getByTestId('home-last-expenses-section')).toContainText(category)
})

test('home: export excel triggers download', async ({ page }) => {
  await page.goto('/')

  const downloadPromise = page.waitForEvent('download')
  await page.getByTestId('home-export-excel').click()

  const download = await downloadPromise
  expect(download.suggestedFilename()).toMatch(/\.(xlsx|xls|csv)$/i)
})

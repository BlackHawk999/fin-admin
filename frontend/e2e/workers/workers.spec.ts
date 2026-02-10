import { test, expect } from '@playwright/test'

function uniq(prefix = 'E2E') {
  return `${prefix} ${Date.now()}`
}

async function goToWorkers(page: any) {
  await page.goto('/')

  const link = page.getByRole('link', { name: /^Ishchilar$/i })
  await expect(link).toBeVisible()
  await link.click()

  await expect(page.getByTestId('workers-page')).toBeVisible()
}

async function waitWorkerModalVisible(page: any) {
  await page.waitForSelector('[data-testid="worker-modal"]', { state: 'visible', timeout: 5000 })
}
async function waitWorkerModalHidden(page: any) {
  await page.waitForSelector('[data-testid="worker-modal"]', { state: 'hidden', timeout: 5000 })
}

test('workers: create -> appears in table', async ({ page }) => {
  await goToWorkers(page)

  await page.getByTestId('worker-add').click()
  await waitWorkerModalVisible(page)

  const name = uniq('E2E worker')
  await page.getByTestId('worker-full-name').fill(name)
  await page.getByTestId('worker-salary').fill('500000')

  await page.getByTestId('worker-submit').click()
  await waitWorkerModalHidden(page)

  await expect(page.getByTestId('workers-table')).toContainText(name)
})

test('workers: search filters list', async ({ page }) => {
  await goToWorkers(page)

  // создаём работника для поиска
  await page.getByTestId('worker-add').click()
  await waitWorkerModalVisible(page)

  const name = uniq('E2E find')
  await page.getByTestId('worker-full-name').fill(name)
  await page.getByTestId('worker-salary').fill('400000')

  await page.getByTestId('worker-submit').click()
  await waitWorkerModalHidden(page)

  await expect(page.getByTestId('workers-table')).toContainText(name)

  // поиск
  await page.getByTestId('workers-search').fill(name)
  await expect(page.getByTestId('workers-table')).toContainText(name)
})

test('workers: open detail page from list', async ({ page }) => {
  await goToWorkers(page)

  // если есть хоть один worker-open-* — откроем первого
  const openLink = page.locator('[data-testid^="worker-open-"]').first()
  await expect(openLink).toBeVisible()
  await openLink.click()

  await expect(page.getByTestId('worker-detail-page')).toBeVisible()
})

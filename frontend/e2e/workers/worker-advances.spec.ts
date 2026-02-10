import { test, expect } from '@playwright/test'

function uniq(prefix = 'E2E') {
  return `${prefix} ${Date.now()}`
}

async function goToAnyWorkerDetail(page: any) {
  await page.goto('/')

  const link = page.getByRole('link', { name: /^Ishchilar$/i })
  await expect(link).toBeVisible()
  await link.click()
  await expect(page.getByTestId('workers-page')).toBeVisible()

  const openLink = page.locator('[data-testid^="worker-open-"]').first()
  await expect(openLink).toBeVisible()
  await openLink.click()

  await expect(page.getByTestId('worker-detail-page')).toBeVisible()
}

async function waitAdvanceModalVisible(page: any) {
  await page.waitForSelector('[data-testid="advance-modal"]', { state: 'visible', timeout: 5000 })
}
async function waitAdvanceModalHidden(page: any) {
  await page.waitForSelector('[data-testid="advance-modal"]', { state: 'hidden', timeout: 5000 })
}

test('worker detail: add advance -> appears in table', async ({ page }) => {
  await goToAnyWorkerDetail(page)

  await page.getByTestId('advance-add').click()
  await waitAdvanceModalVisible(page)

  const comment = uniq('E2E advance')
  await page.getByTestId('advance-amount').fill('30000')
  await page.getByTestId('advance-comment').fill(comment)

  await page.getByTestId('advance-submit').click()
  await waitAdvanceModalHidden(page)

  await expect(page.getByTestId('worker-advances-table')).toContainText(comment)
})

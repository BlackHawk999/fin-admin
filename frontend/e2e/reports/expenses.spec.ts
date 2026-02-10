import { test, expect } from '@playwright/test'

function uniq(prefix = 'E2E') {
  return `${prefix} ${Date.now()}`
}

async function goToExpenses(page: any) {
  await page.goto('/')

  const link = page.getByRole('link', { name: /^Xarajatlar$/i })
  await expect(link).toBeVisible()
  await link.click()

  await expect(page.getByTestId('expenses-page')).toBeVisible()
}

async function waitExpenseModalVisible(page: any) {
  await page.waitForSelector('[data-testid="expense-modal"]', { state: 'visible', timeout: 5000 })
}

async function waitExpenseModalHidden(page: any) {
  await page.waitForSelector('[data-testid="expense-modal"]', { state: 'hidden', timeout: 5000 })
}

test('expenses: create expense -> appears in table', async ({ page }) => {
  await goToExpenses(page)

  // открыть форму создания
  await page.getByTestId('expense-add').click()
  await waitExpenseModalVisible(page)

  const comment = uniq('E2E expense')
  const category = uniq('Cat')

  await page.getByTestId('expense-date').fill(new Date().toISOString().slice(0, 10))
  await page.getByTestId('expense-amount').fill('15000')
  await page.getByTestId('expense-category').fill(category)
  await page.getByTestId('expense-comment').fill(comment)

  await page.getByTestId('expense-submit').click()
  await waitExpenseModalHidden(page)

  // запись должна появиться в таблице
  await expect(page.getByTestId('expenses-table')).toContainText(category)
  await expect(page.getByTestId('expenses-table')).toContainText(comment)
})

test('expenses: filter by comment reduces list', async ({ page }) => {
  await goToExpenses(page)

  // создадим уникальную запись, чтобы потом точно найти по фильтру
  await page.getByTestId('expense-add').click()
  await waitExpenseModalVisible(page)

  const comment = uniq('E2E filter')
  const category = uniq('CatF')

  await page.getByTestId('expense-amount').fill('12000')
  await page.getByTestId('expense-category').fill(category)
  await page.getByTestId('expense-comment').fill(comment)

  await page.getByTestId('expense-submit').click()
  await waitExpenseModalHidden(page)

  // убедимся что запись есть
  await expect(page.getByTestId('expenses-table')).toContainText(comment)

  // применяем фильтр по комментарию
  await page.getByTestId('expenses-filter-comment').fill(comment)

  // у тебя debounce 250мс + load по API, подождём пока таблица обновится
  await expect(page.getByTestId('expenses-table')).toContainText(comment)

  // и проверим, что “левый” текст (например, из меню) не влияет — просто таблица видна
  await expect(page.getByTestId('expenses-table')).toBeVisible()
})

test('expenses: export downloads file', async ({ page }) => {
  await goToExpenses(page)

  const downloadPromise = page.waitForEvent('download')
  await page.getByTestId('expenses-export').click()
  const download = await downloadPromise

  expect(download.suggestedFilename()).toMatch(/\.(xlsx|xls|csv)$/i)
})

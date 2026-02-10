import { test, expect } from '@playwright/test'

function uniq(prefix = 'E2E') {
  return `${prefix} ${Date.now()}`
}

async function goToCompanies(page: any) {
  await page.goto('/')

  // В UI у тебя заголовок "Firmalar", но ссылка может называться Kompaniyalar/Firmalar.
  // Берём самый надёжный вариант — кликаем по ссылке, где есть Firmalar или Kompaniyalar.
  const link = page.getByRole('link', { name: /Firmalar|Kompaniyalar/i }).first()
  await expect(link).toBeVisible()
  await link.click()

  await expect(page.getByTestId('companies-page')).toBeVisible()
}

async function waitCompanyModalVisible(page: any) {
  await page.waitForSelector('[data-testid="company-modal"]', { state: 'visible', timeout: 5000 })
}
async function waitCompanyModalHidden(page: any) {
  await page.waitForSelector('[data-testid="company-modal"]', { state: 'hidden', timeout: 5000 })
}

test('companies: create company -> appears in table', async ({ page }) => {
  await goToCompanies(page)

  await page.getByTestId('company-add').click()
  await waitCompanyModalVisible(page)

  const name = uniq('E2E company')
  await page.getByTestId('company-name').fill(name)

  await page.getByTestId('company-submit').click()
  await waitCompanyModalHidden(page)

  await expect(page.getByTestId('companies-table')).toContainText(name)
})

test('companies: search filters list', async ({ page }) => {
  await goToCompanies(page)

  // создадим компанию, чтобы точно было что искать
  await page.getByTestId('company-add').click()
  await waitCompanyModalVisible(page)

  const name = uniq('E2E search')
  await page.getByTestId('company-name').fill(name)

  await page.getByTestId('company-submit').click()
  await waitCompanyModalHidden(page)

  await expect(page.getByTestId('companies-table')).toContainText(name)

  // поиск
  await page.getByTestId('companies-search').fill(name)
  await expect(page.getByTestId('companies-table')).toContainText(name)
})

test('companies: active filter can be changed', async ({ page }) => {
  await goToCompanies(page)

  // просто переключаем фильтр — проверяем, что таблица остаётся видимой
  await page.getByTestId('companies-filter-active').selectOption({ label: 'Faol' }).catch(async () => {
    // если label не совпал — попробуем по value
    await page.getByTestId('companies-filter-active').selectOption('true')
  })

  await expect(page.getByTestId('companies-table-wrap')).toBeVisible()

  await page.getByTestId('companies-filter-active').selectOption({ label: 'Nofaol' }).catch(async () => {
    await page.getByTestId('companies-filter-active').selectOption('false')
  })

  await expect(page.getByTestId('companies-table-wrap')).toBeVisible()

  // вернём "Barchasi"
  await page.getByTestId('companies-filter-active').selectOption({ label: 'Barchasi' }).catch(async () => {
    await page.getByTestId('companies-filter-active').selectOption('')
  })
})

import { test, expect } from '@playwright/test'

function uniq(prefix = 'E2E') {
  return `${prefix} ${Date.now()}`
}

/**
 * Переход на страницу "Кассы" через меню, чтобы не зависеть от роутов.
 * В твоём UI есть пункт "Kassalar" — используем его.
 */
async function goToCashboxes(page: any) {
  await page.goto('/')

  const kassalarLink = page.getByRole('link', { name: /^Kassalar$/i })
  await expect(kassalarLink).toBeVisible()
  await kassalarLink.click()

  await expect(page.getByTestId('cashboxes-page')).toBeVisible()
}

/**
 * Для модалок (часто Teleport + анимации) надёжнее ждать через waitForSelector
 */
async function waitEntryModalVisible(page: any) {
  await page.waitForSelector('[data-testid="cashbox-entry-modal"]', {
    state: 'visible',
    timeout: 1000,
  })
}

async function waitEntryModalHidden(page: any) {
  await page.waitForSelector('[data-testid="cashbox-entry-modal"]', {
    state: 'hidden',
    timeout: 1000,
  })
}

test('cashbox: create entry -> appears in table', async ({ page }) => {
  await goToCashboxes(page)

  const addBtn = page.locator('[data-testid^="cashbox-add-entry-"]').first()
  await expect(addBtn).toBeVisible()
  await addBtn.click()

  await waitEntryModalVisible(page)

  const comment = uniq('E2E create')

  await page.getByTestId('entry-amount').fill('10000')
  await page.getByTestId('entry-comment').fill(comment)
  await page.getByTestId('entry-submit').click()

  await waitEntryModalHidden(page)

  const anyTable = page.locator('[data-testid^="cashbox-table-"]').first()
  await expect(anyTable).toContainText(comment)
})

test('cashbox: create then edit -> requires reason, old snapshot stays stable', async ({ page }) => {
  await goToCashboxes(page)

  // 1) Создаём запись
  const addBtn = page.locator('[data-testid^="cashbox-add-entry-"]').first()
  await expect(addBtn).toBeVisible()
  await addBtn.click()

  await waitEntryModalVisible(page)

  const comment = uniq('E2E for edit')
  await page.getByTestId('entry-amount').fill('12000')
  await page.getByTestId('entry-comment').fill(comment)
  await page.getByTestId('entry-submit').click()

  await waitEntryModalHidden(page)

  const table = page.locator('[data-testid^="cashbox-table-"]').first()
  await expect(table).toContainText(comment)

  // 2) Находим строку по тексту comment и жмём "Изменить" в этой строке
  const rowTr = page.locator('tr', { hasText: comment }).first()

  if (await rowTr.count()) {
    await rowTr.getByRole('button', { name: /Изменить/i }).click()
  } else {
    const rowAny = page.locator(':is(div,li)', { hasText: comment }).first()
    await expect(rowAny).toBeVisible()
    await rowAny.getByRole('button', { name: /Изменить/i }).click()
  }

  await waitEntryModalVisible(page)

  // Старые значения должны быть видны
  await expect(page.getByTestId('cashbox-old-values')).toBeVisible()

  // Сохраняем без причины -> должна быть ошибка
  await page.getByTestId('entry-submit').click()
  await expect(page.getByText(/Причина обязательна/i)).toBeVisible()

  // Запоминаем старый комментарий из snapshot
  const oldSnapshotComment = await page.getByTestId('cashbox-old-comment').innerText()

  // Меняем комментарий и вводим причину
  const edited = uniq('E2E edited')
  await page.getByTestId('entry-comment').fill(edited)
  await page.getByTestId('entry-edit-reason').fill('E2E: исправление')

  // Snapshot старого комментария не должен меняться
  await expect(page.getByTestId('cashbox-old-comment')).toHaveText(oldSnapshotComment)

  // Сохраняем
  await page.getByTestId('entry-submit').click()
  await waitEntryModalHidden(page)

  // Проверяем, что в таблице появился новый текст
  await expect(table).toContainText(edited)
})

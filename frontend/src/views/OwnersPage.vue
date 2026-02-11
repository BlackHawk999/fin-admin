<template>
  <div class="owners-page">
    <div class="page-header">
      <h1 class="page-header__title">Boshliqlar</h1>
      <button type="button" class="btn btn_primary" @click="openCreate">
        Qo'shish
      </button>
    </div>

    <div class="owners-page__table-wrap">
      <BaseTable
        :columns="columns"
        :data="owners"
        row-key="id"
        actions
      >
        <template #cell="{ column, value }">
          <template v-if="column.key === 'color_hex'">
            <span
              class="owners-page__color"
              :style="{ background: String(value || '') }"
            />
            {{ value ?? '—' }}
          </template>
          <template v-else>
            {{ value ?? '—' }}
          </template>
        </template>

        <template #actions="{ row }">
          <button
            type="button"
            class="btn btn_secondary btn_sm"
            @click="editOwner(row as Owner)"
          >
            Tahrirlash
          </button>

          <button
            type="button"
            class="btn btn_danger btn_sm"
            @click="deleteOwner(row as Owner)"
          >
            O'chirish
          </button>
        </template>
      </BaseTable>
    </div>

    <BaseModal
      v-model="showModal"
      :title="editingId ? 'Tahrirlash' : 'Yangi boshliq'"
    >
      <form class="form">
        <BaseInput v-model="form.name" label="Ism" />
        <BaseInput
          v-model="form.color_hex"
          label="Rangi (HEX)"
          placeholder="#808080"
        />
      </form>

      <template #footer>
        <button
          type="button"
          class="btn btn_secondary"
          @click="showModal = false"
        >
          Bekor qilish
        </button>

        <button
          type="button"
          class="btn btn_primary"
          @click="save"
        >
          Saqlash
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  fetchOwners,
  createOwner,
  updateOwner,
  deleteOwner as apiDeleteOwner,
} from '@/api/owners'

import BaseTable from '@/components/BaseTable/BaseTable.vue'
import type { Column } from '@/components/BaseTable/BaseTable.vue'
import BaseInput from '@/components/BaseInput/BaseInput.vue'
import BaseModal from '@/components/BaseModal/BaseModal.vue'
import type { Owner } from '@/types'

const columns: Column[] = [
  { key: 'name', label: 'Имя' },
  { key: 'color_hex', label: 'Цвет' },
]

const owners = ref<Owner[]>([])
const showModal = ref(false)
const editingId = ref<number | null>(null)

const form = ref({
  name: '',
  color_hex: '#808080',
})

async function load() {
  const { data } = await fetchOwners()
  owners.value = data
}

function openCreate() {
  editingId.value = null
  form.value = {
    name: '',
    color_hex: '#808080',
  }
  showModal.value = true
}

function editOwner(row: Owner) {
  editingId.value = row.id
  form.value = {
    name: row.name,
    color_hex: row.color_hex,
  }
  showModal.value = true
}

async function save() {
  if (editingId.value) {
    await updateOwner(editingId.value, form.value)
  } else {
    await createOwner(form.value)
  }

  showModal.value = false
  await load()
}

async function deleteOwner(row: Owner) {
  if (!confirm(`Удалить владельца "${row.name}"?`)) return
  await apiDeleteOwner(row.id)
  await load()
}

onMounted(load)
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.owners-page {
  &__table-wrap {
    background: $bg-card;
    border-radius: $radius;
    overflow: hidden;
    box-shadow: $shadow;
  }

  &__color {
    display: inline-block;
    width: 16px;
    height: 16px;
    border-radius: 3px;
    margin-right: 0.5rem;
    vertical-align: middle;
    border: 1px solid $border-color;
  }
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>

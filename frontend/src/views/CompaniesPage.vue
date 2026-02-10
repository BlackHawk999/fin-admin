<template>
  <div class="companies-page" data-testid="companies-page">
    <div class="page-header">
      <h1 class="page-header__title">Firmalar</h1>
      <button type="button" class="btn btn_primary" @click="openCreate" data-testid="company-add">
        Qo'shish
      </button>
    </div>

    <div class="companies-page__filters" data-testid="companies-filters">
      <BaseInput v-model="search" placeholder="Qidirish" data-testid="companies-search" />
      <select v-model="filterActive" class="companies-page__select" data-testid="companies-filter-active">
        <option :value="null">Barchasi</option>
        <option :value="true">Faol</option>
        <option :value="false">Nofaol</option>
      </select>
    </div>

    <div class="companies-page__table-wrap" data-testid="companies-table-wrap">
      <div data-testid="companies-table">
        <BaseTable :columns="columns" :data="companies" row-key="id" actions>
          <template #cell="{ column, value }">
            <template v-if="column.key === 'is_active'">{{ value ? 'Ha' : "Yuq" }}</template>
            <template v-else>{{ value }}</template>
          </template>

          <template #actions="{ row }">
            <router-link
              :to="`/companies/${row.id}`"
              class="btn btn_secondary btn_sm"
              :data-testid="`company-open-${row.id}`"
            >
              Ochish
            </router-link>
          </template>
        </BaseTable>
      </div>
    </div>

    <BaseModal
      v-model="showModal"
      :title="editingId ? 'Tahrirlash' : 'Yangi firma'"
      @update:model-value="showModal = false"
      data-testid="company-modal"
    >
      <form class="form" data-testid="company-form">
        <BaseInput v-model="form.name" label="Nomlanishi" data-testid="company-name" />
        <label class="form__checkbox" data-testid="company-active">
          <input v-model="form.is_active" type="checkbox" data-testid="company-active-checkbox" />
          Faol
        </label>
      </form>

      <template #footer>
        <button type="button" class="btn btn_secondary" @click="showModal = false" data-testid="company-cancel">
          Bekor qilish
        </button>
        <button type="button" class="btn btn_primary" @click="save" data-testid="company-submit">
          Saqlash
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { fetchCompanies, createCompany, updateCompany } from '@/api/companies'
import BaseTable from '@/components/BaseTable/BaseTable.vue'
import type { Column } from '@/components/BaseTable/BaseTable.vue'
import BaseInput from '@/components/BaseInput/BaseInput.vue'
import BaseModal from '@/components/BaseModal/BaseModal.vue'
import type { Company } from '@/types'

const columns: Column[] = [
  { key: 'name', label: 'Название' },
  { key: 'is_active', label: 'Активна' },
]

const companies = ref<Company[]>([])
const search = ref('')
const filterActive = ref<boolean | null>(null)
const showModal = ref(false)
const editingId = ref<number | null>(null)
const form = ref({ name: '', is_active: true })

function openCreate() {
  editingId.value = null
  form.value = { name: '', is_active: true }
  showModal.value = true
}

async function load() {
  const { data } = await fetchCompanies({
    search: search.value || undefined,
    is_active: filterActive.value ?? undefined,
  })
  companies.value = data
}

async function save() {
  if (editingId.value) {
    await updateCompany(editingId.value, form.value)
  } else {
    await createCompany(form.value)
  }
  showModal.value = false
  load()
}

watch([search, filterActive], load)
onMounted(load)
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.companies-page {
  &__filters {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
  }
  &__select {
    padding: 0.5rem 0.75rem;
    border: 1px solid $border-color;
    border-radius: 4px;
  }
  &__table-wrap {
    background: $bg-card;
    border-radius: $radius;
    overflow: hidden;
    box-shadow: $shadow;
  }
}

.form__checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}
</style>

<template>
  <div class="workers-page" data-testid="workers-page">
    <div class="page-header">
      <h1 class="page-header__title">Ishchilar</h1>
      <button
        type="button"
        class="btn btn_primary"
        @click="openCreate"
        data-testid="worker-add"
      >
        Qo'shish
      </button>
    </div>

    <div class="workers-page__filters" data-testid="workers-filters">
      <BaseInput
        v-model="search"
        placeholder="Ism bo'yicha izlash"
        class="workers-page__search"
        data-testid="workers-search"
      />

      <select
        v-model="filterActive"
        class="workers-page__select"
        data-testid="workers-filter-active"
      >
        <option :value="null">Barchasi</option>
        <option :value="true">Faol</option>
        <option :value="false">Nofaol</option>
      </select>
    </div>

    <div class="workers-page__table-wrap" data-testid="workers-table-wrap">
      <div data-testid="workers-table">
        <BaseTable :columns="columns" :data="employees" row-key="id" actions>
          <template #cell="{ column, value }">
            <template v-if="column.key === 'monthly_salary_uzs'">{{
              formatUzs(value)
            }}</template>
            <template v-else-if="column.key === 'is_active'">{{
              value ? "Да" : "Нет"
            }}</template>
            <template v-else>{{ value }}</template>
          </template>

          <template #actions="{ row }">
            <router-link
              :to="`/workers/${row.id}`"
              class="btn btn_secondary btn_sm"
              :data-testid="`worker-open-${row.id}`"
            >
              Ochish
            </router-link>
          </template>
        </BaseTable>
      </div>
    </div>

    <BaseModal
      v-model="showModal"
      :title="editingId ? 'Tahrirlash' : 'Yangi ishchi'"
      @update:model-value="onCloseModal"
      data-testid="worker-modal"
    >
      <form class="form" @submit.prevent="save" data-testid="worker-form">
        <BaseInput
          v-model="form.full_name"
          label="ФИО"
          data-testid="worker-full-name"
        />
        <MoneyInput
          v-model="form.monthly_salary_uzs"
          label="Oylik (сум/мес)"
          data-testid="worker-salary"
        />

        <label class="form__checkbox" data-testid="worker-active">
          <input
            v-model="form.is_active"
            type="checkbox"
            data-testid="worker-active-checkbox"
          />
          Faol
        </label>
      </form>

      <template #footer>
        <button
          type="button"
          class="btn btn_secondary"
          @click="showModal = false"
          data-testid="worker-cancel"
        >
          Bekor qilish
        </button>
        <button
          type="button"
          class="btn btn_primary"
          @click="save"
          data-testid="worker-submit"
        >
          Saqlash
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import {
  fetchEmployees,
  createEmployee,
  updateEmployee,
} from "@/api/employees";
import { formatUzs } from "@/utils/format";
import BaseTable from "@/components/BaseTable/BaseTable.vue";
import type { Column } from "@/components/BaseTable/BaseTable.vue";
import BaseInput from "@/components/BaseInput/BaseInput.vue";
import MoneyInput from "@/components/MoneyInput/MoneyInput.vue";
import BaseModal from "@/components/BaseModal/BaseModal.vue";
import type { Employee } from "@/types";

const columns: Column[] = [
  { key: "full_name", label: "ФИО" },
  { key: "monthly_salary_uzs", label: "Зарплата" },
  { key: "is_active", label: "Активен" },
];

const employees = ref<Employee[]>([]);
const search = ref("");
const filterActive = ref<boolean | null>(null);
const showModal = ref(false);
const editingId = ref<number | null>(null);
const form = ref({ full_name: "", monthly_salary_uzs: 0, is_active: true });

function openCreate() {
  editingId.value = null;
  form.value = { full_name: "", monthly_salary_uzs: 0, is_active: true };
  showModal.value = true;
}

function onCloseModal() {
  showModal.value = false;
}

async function load() {
  const { data } = await fetchEmployees({
    search: search.value || undefined,
    is_active: filterActive.value ?? undefined,
  });
  employees.value = data;
}

async function save() {
  if (editingId.value) {
    await updateEmployee(editingId.value, form.value);
  } else {
    await createEmployee(form.value);
  }
  showModal.value = false;
  load();
}

watch([search, filterActive], load);
onMounted(load);
</script>

<style lang="scss" scoped>
@use "@/styles/variables" as *;

.workers-page {
  &__filters {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  &__search {
    max-width: 280px;
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

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  &__checkbox {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
  }
}
</style>

<template>
  <div class="base-table">
    <table class="base-table__table">
      <thead class="base-table__head">
        <tr class="base-table__row base-table__row_head">
          <th
            v-for="col in columns"
            :key="col.key"
            class="base-table__cell base-table__cell_head"
            :class="col.thClass"
          >
            {{ col.label }}
          </th>
          <th v-if="actions" class="base-table__cell base-table__cell_head base-table__cell_actions"></th>
        </tr>
      </thead>
      <tbody class="base-table__body">
        <tr
          v-for="(row, idx) in data"
          :key="rowKey ? (row as Record<string, unknown>)[rowKey] : idx"
          class="base-table__row"
        >
          <td
            v-for="col in columns"
            :key="col.key"
            class="base-table__cell"
            :class="col.tdClass"
          >
            <slot name="cell" :column="col" :row="row" :value="(row as Record<string, unknown>)[col.key]">
              {{ (row as Record<string, unknown>)[col.key] }}
            </slot>
          </td>
          <td v-if="actions" class="base-table__cell base-table__cell_actions">
            <slot name="actions" :row="row"></slot>
          </td>
        </tr>
      </tbody>
      <tfoot v-if="summary !== undefined" class="base-table__foot">
        <tr class="base-table__row base-table__row_foot">
          <td :colspan="columns.length + (actions ? 1 : 0)" class="base-table__cell base-table__cell_foot">
            <slot name="summary" :summary="summary">{{ summary }}</slot>
          </td>
        </tr>
      </tfoot>
    </table>
  </div>
</template>

<script setup lang="ts">
export interface Column {
  key: string
  label: string
  thClass?: string
  tdClass?: string
}

defineProps<{
  columns: Column[]
  data: unknown[]
  rowKey?: string
  actions?: boolean
  summary?: string | number
}>()
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.base-table {
  overflow-x: auto;
  background: $bg-card;
  border-radius: $radius;
  box-shadow: $shadow;

  &__table {
    min-width: 100%;
  }

  &__head {
    background: #f9fafb;
    border-bottom: 1px solid $border-color;
  }

  &__row {
    &_head .base-table__cell {
      font-weight: 600;
      padding: 0.75rem 1rem;
      text-align: left;
    }
    &_foot .base-table__cell {
      font-weight: 600;
      border-top: 2px solid $border-color;
    }
  }

  &__cell {
    padding: 0.6rem 1rem;
    border-bottom: 1px solid #f0f0f0;

    &_head {
      white-space: nowrap;
    }
    &_actions {
      width: 1%;
      white-space: nowrap;
    }
    &_right {
      text-align: right;
    }
    &_foot {
      padding: 0.75rem 1rem;
    }
  }

  &__body .base-table__row:hover {
    background: #fafafa;
  }
}
</style>

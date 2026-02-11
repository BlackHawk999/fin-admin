<template>
  <div class="app-layout">
    <aside class="app-layout__sidebar">
      <nav class="sidebar-nav">
        <ul class="sidebar-nav__list">
          <li class="sidebar-nav__item">
            <router-link
              class="sidebar-nav__link"
              :class="{ 'sidebar-nav__link_active': isActive('/') }"
              to="/"
            >
              Home
            </router-link>
          </li>

          <li class="sidebar-nav__item">
            <router-link
              class="sidebar-nav__link"
              :class="{ 'sidebar-nav__link_active': isActive('/expenses') }"
              to="/expenses"
            >
              Xarajatlar
            </router-link>
          </li>

          <li class="sidebar-nav__item">
            <router-link
              class="sidebar-nav__link"
              :class="{ 'sidebar-nav__link_active': isStartsWith('/workers') }"
              to="/workers"
            >
              Ishchilar
            </router-link>
          </li>

          <li class="sidebar-nav__item">
            <router-link
              class="sidebar-nav__link"
              :class="{ 'sidebar-nav__link_active': isStartsWith('/companies') }"
              to="/companies"
            >
              Kompaniyalar
            </router-link>
          </li>

          <li class="sidebar-nav__item">
            <router-link
              class="sidebar-nav__link"
              :class="{ 'sidebar-nav__link_active': isActive('/cashboxes') }"
              to="/cashboxes"
            >
              Kassalar
            </router-link>
          </li>

          <li class="sidebar-nav__item">
            <router-link
              class="sidebar-nav__link"
              :class="{ 'sidebar-nav__link_active': isActive('/owners') }"
              to="/owners"
            >
              Boshliqlar / Kategoriyalar
            </router-link>
          </li>

          <li class="sidebar-nav__item">
            <router-link
              class="sidebar-nav__link"
              :class="{ 'sidebar-nav__link_active': isActive('/settings') }"
              to="/settings"
            >
              Settings
            </router-link>
          </li>
        </ul>
      </nav>
    </aside>

    <div class="app-layout__body">
      <header class="topbar app-layout__topbar">
        <h1 class="topbar__title">Fin Admin</h1>
        <TopbarDateRange class="topbar__daterange" />

        <div class="topbar__profile">
          <span class="topbar__profile-name">Admin</span>
          <button type="button" class="topbar__logout" aria-label="Выход" @click="logout">Выход</button>
        </div>
      </header>

      <main class="app-layout__content">
        <router-view />
      </main>
    </div>

    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import TopbarDateRange from '@/components/TopbarDateRange/TopbarDateRange.vue'
import ToastContainer from '@/components/Toast/ToastContainer.vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const currentPath = computed(() => route.path)

function isActive(path: string) {
  return currentPath.value === path
}

function isStartsWith(prefix: string) {
  return currentPath.value.startsWith(prefix)
}

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.app-layout {
  display: flex;
  min-height: 100vh;

  &__sidebar {
    width: 220px;
    flex-shrink: 0;
    background: $bg-sidebar;
    border-right: 1px solid $border-color;
    padding: 1rem 0;
  }

  &__body {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  &__topbar {
    flex-shrink: 0;
  }

  &__content {
    flex: 1;
    padding: 1.5rem;
    overflow-x: auto;
  }
}

.sidebar-nav {
  &__list {
    display: flex;
    flex-direction: column;
    gap: 5px;
    list-style: none;
    margin: 0;
    padding: 0;
  }

  &__item {
    margin: 0;
  }

  &__link {
    display: block;
    padding: 0.6rem 1rem;
    color: $text-secondary;
    text-decoration: none;
    border-radius: 4px;
    margin: 0 0.5rem;
    transition: background 0.15s, color 0.15s;

    &:hover {
      background: $bg-hover;
      color: $text-primary;
    }

    &_active {
      background: $primary;
      color: #fff;
    }
  }
}

.topbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 0.75rem 1.5rem;
  background: #fff;
  border-bottom: 1px solid $border-color;

  &__title {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
  }

  &__daterange {
    flex: 1;
    min-width: 200px;
    justify-content: center;
  }

  &__profile {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  &__profile-name {
    font-size: 0.875rem;
    color: $text-secondary;
  }

  &__logout {
    padding: 0.35rem 0.6rem;
    border: 1px solid $border-color;
    border-radius: 4px;
    background: #fff;
    font-size: 0.8rem;
    cursor: pointer;
    color: $text-secondary;

    &:hover {
      background: $bg-hover;
      color: $text-primary;
    }
  }
}
</style>

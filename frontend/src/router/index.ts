import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'Login', component: () => import('@/views/LoginPage.vue'), meta: { public: true } },
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'Home', component: () => import('@/views/HomePage.vue') },
        { path: 'workers', name: 'Workers', component: () => import('@/views/WorkersPage.vue') },
        { path: 'workers/:id', name: 'WorkerDetail', component: () => import('@/views/WorkerDetailPage.vue') },
        { path: 'companies', name: 'Companies', component: () => import('@/views/CompaniesPage.vue') },
        { path: 'companies/:id', name: 'CompanyDetail', component: () => import('@/views/CompanyDetailPage.vue') },
        { path: 'cashboxes', name: 'Cashboxes', component: () => import('@/views/CashboxesPage.vue') },
        { path: 'expenses', name: 'Expenses', component: () => import('@/views/ExpensesPage.vue') },
        { path: 'owners', name: 'Owners', component: () => import('@/views/OwnersPage.vue') },
        { path: 'settings', name: 'Settings', component: () => import('@/views/SettingsPage.vue') },
      ],
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login' })
  } else if (to.name === 'Login' && token) {
    next({ path: '/' })
  } else {
    next()
  }
})

export default router

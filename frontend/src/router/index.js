import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', name: 'Dashboard', component: () => import('../views/DashboardView.vue'), meta: { requiresAuth: true } },
  { path: '/login', name: 'Login', component: () => import('../views/LoginView.vue'), meta: { guest: true } },
  { path: '/register', name: 'Register', component: () => import('../views/RegisterView.vue'), meta: { guest: true } },
  { path: '/topics', name: 'Topics', component: () => import('../views/TopicsView.vue'), meta: { requiresAuth: true } },
  { path: '/topics/:id', name: 'TopicDetail', component: () => import('../views/TopicDetailView.vue'), meta: { requiresAuth: true } },
  { path: '/trainer', name: 'TrainerSetup', component: () => import('../views/TrainerSetupView.vue'), meta: { requiresAuth: true } },
  { path: '/trainer/session/:id', name: 'TrainerSession', component: () => import('../views/TrainerSessionView.vue'), meta: { requiresAuth: true } },
  { path: '/trainer/session/:id/results', name: 'TrainerResults', component: () => import('../views/TrainerResultsView.vue'), meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  authStore.loadFromStorage()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/client'

export const useAuthStore = defineStore('auth', () => {
  const access = ref(localStorage.getItem('access') || '')
  const refresh = ref(localStorage.getItem('refresh') || '')
  const email = ref('')

  const isAuthenticated = computed(() => !!access.value)

  function setTokens(data) {
    access.value = data.access
    refresh.value = data.refresh
    email.value = data.email || ''
    localStorage.setItem('access', data.access)
    localStorage.setItem('refresh', data.refresh)
  }

  function loadFromStorage() {
    access.value = localStorage.getItem('access') || ''
    refresh.value = localStorage.getItem('refresh') || ''
  }

  function clear() {
    access.value = ''
    refresh.value = ''
    email.value = ''
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
  }

  async function register(emailVal, password) {
    const { data } = await authApi.register(emailVal, password)
    setTokens(data)
  }

  async function login(emailVal, password) {
    const { data } = await authApi.login(emailVal, password)
    setTokens(data)
  }

  function logout() {
    clear()
  }

  return {
    access,
    email,
    isAuthenticated,
    setTokens,
    loadFromStorage,
    clear,
    register,
    login,
    logout,
  }
})

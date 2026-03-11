<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const isAuthenticated = computed(() => authStore.isAuthenticated)
const theme = ref('light')
const isDarkTheme = computed(() => theme.value === 'dark')
const navigationItems = [
  {
    label: 'Дашборд',
    to: { name: 'Dashboard' },
    names: ['Dashboard'],
  },
  {
    label: 'Теми',
    to: { name: 'Topics' },
    names: ['Topics', 'TopicDetail'],
  },
  {
    label: 'Тренажер',
    to: { name: 'TrainerSetup' },
    names: ['TrainerSetup', 'TrainerSession', 'TrainerResults'],
  },
]

function logout() {
  authStore.logout()
  router.push('/login')
}

function isActiveLink(names) {
  return names.includes(route.name)
}

function applyTheme(nextTheme) {
  const normalizedTheme = nextTheme === 'dark' ? 'dark' : 'light'
  theme.value = normalizedTheme
  document.documentElement.setAttribute('data-theme', normalizedTheme)
}

function toggleTheme() {
  applyTheme(theme.value === 'dark' ? 'light' : 'dark')
}

onMounted(() => {
  const savedTheme = localStorage.getItem('studyit-theme')
  if (savedTheme === 'dark' || savedTheme === 'light') {
    applyTheme(savedTheme)
    return
  }

  const prefersDark =
    typeof window !== 'undefined' &&
    typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-color-scheme: dark)').matches

  applyTheme(prefersDark ? 'dark' : 'light')
})

watch(theme, (value) => {
  localStorage.setItem('studyit-theme', value)
})
</script>

<template>
  <div class="min-h-screen flex flex-col font-sans">
    <div v-if="!isAuthenticated" class="fixed right-4 top-4 z-30">
      <button
        type="button"
        class="theme-toggle"
        :class="isDarkTheme ? 'theme-toggle-dark' : 'theme-toggle-light'"
        :aria-label="isDarkTheme ? 'Увімкнути світлу тему' : 'Увімкнути темну тему'"
        :title="isDarkTheme ? 'Світла тема' : 'Темна тема'"
        @click="toggleTheme"
      >
        <span class="theme-toggle-track">
          <span class="theme-toggle-icon theme-toggle-icon-sun" aria-hidden="true">☀</span>
          <span class="theme-toggle-icon theme-toggle-icon-moon" aria-hidden="true">☾</span>
          <span class="theme-toggle-thumb" aria-hidden="true" />
        </span>
      </button>
    </div>
    <nav v-if="isAuthenticated" class="border-b-4 border-black bg-white sticky top-0 z-20 shadow-[0_4px_0_0_rgba(0,0,0,1)] mb-8">
      <div class="w-full max-w-[1180px] mx-auto px-4 py-3 flex flex-col md:flex-row items-center justify-center md:justify-between gap-4">
        <div class="flex items-center justify-center md:justify-start gap-4 w-full md:w-auto">
          <button
            type="button"
            class="theme-toggle shrink-0"
            :class="isDarkTheme ? 'theme-toggle-dark' : 'theme-toggle-light'"
            :aria-label="isDarkTheme ? 'Увімкнути світлу тему' : 'Увімкнути темну тему'"
            :title="isDarkTheme ? 'Світла тема' : 'Темна тема'"
            @click="toggleTheme"
          >
            <span class="theme-toggle-track">
              <span class="theme-toggle-icon theme-toggle-icon-sun" aria-hidden="true">☀</span>
              <span class="theme-toggle-icon theme-toggle-icon-moon" aria-hidden="true">☾</span>
              <span class="theme-toggle-thumb" aria-hidden="true" />
            </span>
          </button>
          
          <router-link :to="{ name: 'Dashboard' }" class="flex items-center gap-3 group shrink-0">
            <div class="w-10 h-10 bg-[#bbf7d0] group-hover:bg-[#fef08a] transition-colors rounded-xl border-[3px] border-black flex items-center justify-center shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] group-hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] group-hover:-translate-y-0.5 group-hover:-translate-x-0.5 group-active:translate-y-0 group-active:translate-x-0 group-active:shadow-[0px_0px_0px_0px_rgba(0,0,0,1)]">
              <div class="w-4 h-4 bg-black rounded-full"></div>
            </div>
            <span class="font-display font-black text-2xl tracking-tight uppercase" style="text-shadow: 2px 2px 0px rgba(0,0,0,0.15);">StudyIt</span>
          </router-link>
        </div>
        
        <div class="flex flex-wrap justify-center items-center gap-2 md:gap-3 w-full md:w-auto">
          <router-link
            v-for="item in navigationItems"
            :key="item.label"
            :to="item.to"
            class="px-5 py-2 rounded-full border-[3px] border-black font-display font-bold text-sm transition-all"
            :class="[
              isActiveLink(item.names)
                ? 'bg-[#c7d2fe] text-black shadow-[4px_4px_0px_0px_#000] -translate-y-[2px] -translate-x-[2px]'
                : 'bg-white hover:bg-[#fef08a] shadow-[0px_0px_0px_0px_#000] hover:shadow-[4px_4px_0px_0px_#000] hover:-translate-y-[2px] hover:-translate-x-[2px] active:translate-y-0 active:translate-x-0 active:shadow-[0px_0px_0px_0px_#000]'
            ]"
          >
            {{ item.label }}
          </router-link>
          
          <button 
            @click="logout"
            class="md:ml-2 px-5 py-2 rounded-full border-[3px] border-black bg-black text-white font-display font-bold text-sm transition-all hover:bg-gray-800 shadow-[4px_4px_0px_0px_#cbd5e1] hover:-translate-y-[2px] hover:-translate-x-[2px] active:translate-y-0 active:translate-x-0 active:shadow-[0px_0px_0px_0px_#cbd5e1]"
          >
            Вийти
          </button>
        </div>
      </div>
    </nav>
    <main class="flex-1 w-full max-w-[1180px] mx-auto p-4 md:px-8 md:pb-12" :class="{ 'flex items-center justify-center h-screen': !isAuthenticated }">
      <RouterView />
    </main>
  </div>
</template>

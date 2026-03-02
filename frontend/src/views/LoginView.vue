<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const email = ref('')
const password = ref('')
const error = ref('')
const authStore = useAuthStore()
const router = useRouter()

async function submit() {
  error.value = ''
  try {
    await authStore.login(email.value, password.value)
    const redirect = router.currentRoute.value.query.redirect || '/'
    router.push(redirect)
  } catch (e) {
    error.value = e.response?.data?.message || 'Помилка входу'
  }
}
</script>

<template>
  <div class="mx-auto max-w-sm rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
    <h1 class="mb-4 text-xl font-semibold">Вхід</h1>
    <form @submit.prevent="submit" class="space-y-4">
      <div>
        <label class="mb-1 block text-sm font-medium">Email</label>
        <input
          v-model="email"
          type="email"
          required
          class="w-full rounded border border-slate-300 px-3 py-2"
        />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">Пароль</label>
        <input
          v-model="password"
          type="password"
          required
          class="w-full rounded border border-slate-300 px-3 py-2"
        />
      </div>
      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
      <button
        type="submit"
        class="w-full rounded bg-slate-800 px-4 py-2 text-white hover:bg-slate-700"
      >
        Увійти
      </button>
    </form>
    <p class="mt-4 text-center text-sm text-slate-600">
      Немає акаунту?
      <router-link to="/register" class="font-medium text-slate-800">Зареєструватися</router-link>
    </p>
  </div>
</template>

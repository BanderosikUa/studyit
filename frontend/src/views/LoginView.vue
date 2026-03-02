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
  <div class="mx-auto max-w-sm rounded-2xl border-[3px] border-black bg-white p-8 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] mt-12">
    <h1 class="mb-6 text-3xl font-display font-black uppercase text-center tracking-tight border-b-2 border-black pb-2">Вхід</h1>
    <form @submit.prevent="submit" class="space-y-5">
      <div>
        <label class="mb-2 block text-sm font-display font-bold uppercase">Email</label>
        <input
          v-model="email"
          type="email"
          required
          class="w-full rounded-xl border-[3px] border-black px-4 py-3 font-sans font-medium focus:outline-none focus:bg-[#fef08a] transition-colors shadow-[2px_2px_0px_0px_#000]"
        />
      </div>
      <div>
        <label class="mb-2 block text-sm font-display font-bold uppercase">Пароль</label>
        <input
          v-model="password"
          type="password"
          required
          class="w-full rounded-xl border-[3px] border-black px-4 py-3 font-sans font-medium focus:outline-none focus:bg-[#fef08a] transition-colors shadow-[2px_2px_0px_0px_#000]"
        />
      </div>
      <p v-if="error" class="text-sm font-bold text-white bg-red-500 border-2 border-black p-2 shadow-[2px_2px_0px_0px_#000]">{{ error }}</p>
      <button
        type="submit"
        class="w-full rounded-xl border-[3px] border-black bg-[#c7d2fe] px-4 py-3 font-display font-bold text-black transition-all shadow-[4px_4px_0px_0px_#000] hover:bg-[#a5b4fc] hover:-translate-y-1 hover:-translate-x-1 hover:shadow-[6px_6px_0px_0px_#000] active:translate-y-0 active:translate-x-0 active:shadow-[0px_0px_0px_0px_#000] text-lg uppercase"
      >
        Увійти
      </button>
    </form>
    <p class="mt-6 text-center text-sm font-medium">
      Немає акаунту?
      <router-link to="/register" class="font-display font-bold text-blue-600 underline decoration-2 underline-offset-2 hover:bg-[#fef08a] hover:text-black transition-colors px-1">Зареєструватися</router-link>
    </p>
  </div>
</template>

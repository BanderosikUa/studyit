<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { topicsApi } from '../api/client'
import { trainerApi } from '../api/client'

const router = useRouter()
const categories = ref([])
const selectedCategory = ref('')
const totalQuestions = ref(10)
const loading = ref(false)
const error = ref('')

onMounted(async () => {
  const { data } = await topicsApi.getCategories()
  categories.value = data
})

async function start() {
  error.value = ''
  loading.value = true
  try {
    const { data } = await trainerApi.createSession(
      selectedCategory.value || null,
      totalQuestions.value
    )
    router.push({ name: 'TrainerSession', params: { id: data.id } })
  } catch (e) {
    error.value = e.response?.data?.message || 'Помилка створення сесії'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-md space-y-8 mt-8">
    <h1 class="text-4xl font-display font-black uppercase tracking-tight text-center">Тренажер</h1>
    <div class="rounded-2xl border-[3px] border-black bg-white p-8 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">
      <div class="space-y-6">
        <div>
          <label class="mb-2 block font-display font-bold uppercase">Категорія</label>
          <select v-model="selectedCategory" class="w-full rounded-xl border-[3px] border-black px-4 py-3 font-sans font-medium focus:outline-none focus:bg-[#fef08a] transition-colors shadow-[2px_2px_0px_0px_#000]">
            <option value="">Усі категорії</option>
            <option v-for="c in categories" :key="c.slug" :value="c.slug">{{ c.name }}</option>
          </select>
        </div>
        <div>
          <label class="mb-2 block font-display font-bold uppercase">Кількість питань</label>
          <input v-model.number="totalQuestions" type="number" min="1" max="50" class="w-full rounded-xl border-[3px] border-black px-4 py-3 font-sans font-medium focus:outline-none focus:bg-[#fef08a] transition-colors shadow-[2px_2px_0px_0px_#000]" />
        </div>
        <p v-if="error" class="text-sm font-bold text-white bg-red-500 border-2 border-black p-2 shadow-[2px_2px_0px_0px_#000]">{{ error }}</p>
        <button
          type="button"
          :disabled="loading"
          class="w-full rounded-xl border-[3px] border-black bg-[#4ade80] px-4 py-3 font-display font-black uppercase text-black text-xl transition-all shadow-[4px_4px_0px_0px_#000] hover:bg-[#22c55e] hover:-translate-y-1 hover:-translate-x-1 hover:shadow-[6px_6px_0px_0px_#000] active:translate-y-0 active:translate-x-0 active:shadow-[0px_0px_0px_0px_#000] disabled:opacity-50 disabled:transform-none disabled:shadow-[4px_4px_0px_0px_#000] mt-4"
          @click="start"
        >
          {{ loading ? 'Завантаження…' : 'Почати' }}
        </button>
      </div>
    </div>
  </div>
</template>

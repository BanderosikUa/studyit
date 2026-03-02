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
  <div class="mx-auto max-w-md space-y-6">
    <h1 class="text-2xl font-semibold">Тренажер</h1>
    <div class="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <div class="space-y-4">
        <div>
          <label class="mb-1 block font-medium">Категорія</label>
          <select v-model="selectedCategory" class="w-full rounded border border-slate-300 px-3 py-2">
            <option value="">Усі категорії</option>
            <option v-for="c in categories" :key="c.slug" :value="c.slug">{{ c.name }}</option>
          </select>
        </div>
        <div>
          <label class="mb-1 block font-medium">Кількість питань</label>
          <input v-model.number="totalQuestions" type="number" min="1" max="50" class="w-full rounded border border-slate-300 px-3 py-2" />
        </div>
        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
        <button
          type="button"
          :disabled="loading"
          class="w-full rounded bg-slate-800 px-4 py-2 text-white hover:bg-slate-700 disabled:opacity-50"
          @click="start"
        >
          {{ loading ? 'Завантаження…' : 'Почати' }}
        </button>
      </div>
    </div>
  </div>
</template>

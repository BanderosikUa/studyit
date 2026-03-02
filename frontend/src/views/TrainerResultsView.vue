<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { trainerApi } from '../api/client'

const route = useRoute()
const session = ref(null)
const prompt = ref('')
const copied = ref(false)

onMounted(async () => {
  const [{ data: sessionData }, { data: promptData }] = await Promise.all([
    trainerApi.getSession(route.params.id),
    trainerApi.getPrompt(route.params.id),
  ])
  session.value = sessionData
  prompt.value = promptData.prompt || ''
})

async function copyPrompt() {
  try {
    await navigator.clipboard.writeText(prompt)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch (_) {}
}
</script>

<template>
  <div class="mx-auto max-w-3xl space-y-6">
    <h1 class="text-2xl font-semibold">Результати тренажера</h1>
    <div v-if="session" class="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h2 class="mb-2 font-medium">Промпт для ChatGPT</h2>
      <p class="mb-3 text-sm text-slate-600">Скопіюйте текст нижче та вставте в ChatGPT для оцінки відповідей.</p>
      <textarea
        :value="prompt"
        readonly
        rows="16"
        class="w-full rounded border border-slate-300 bg-slate-50 px-3 py-2 font-mono text-sm"
      />
      <button
        type="button"
        class="mt-2 rounded bg-slate-800 px-4 py-2 text-white hover:bg-slate-700"
        @click="copyPrompt"
      >
        {{ copied ? 'Скопійовано!' : 'Скопіювати промпт' }}
      </button>
    </div>
  </div>
</template>

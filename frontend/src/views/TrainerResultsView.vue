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
  <div class="mx-auto max-w-3xl space-y-8 mt-6">
    <h1 class="text-4xl font-display font-black uppercase tracking-tight">Результати тренажера</h1>
    <div v-if="session" class="panel-secondary rounded-2xl border-[3px] border-black bg-[#c7d2fe] p-6 md:p-8 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">
      <h2 class="mb-4 font-display font-bold text-2xl uppercase border-b-2 border-black pb-2">Промпт для ChatGPT</h2>
      <p class="mb-6 font-medium text-lg">Скопіюйте текст нижче та вставте в ChatGPT для оцінки відповідей.</p>
      <div class="relative">
        <textarea
          :value="prompt"
          readonly
          rows="16"
          class="w-full rounded-xl border-[3px] border-black bg-[#1e293b] text-white px-4 py-4 font-mono text-sm focus:outline-none shadow-[inset_0_4px_0_0_rgba(0,0,0,0.2)] resize-y"
        />
      </div>
      <button
        type="button"
        class="mt-6 w-full md:w-auto rounded-xl border-[3px] border-black px-8 py-4 font-display font-black uppercase text-lg transition-all shadow-[4px_4px_0px_0px_#000] active:translate-y-0 active:translate-x-0 active:shadow-[0px_0px_0px_0px_#000]"
        :class="copied ? 'bg-[#4ade80] text-black translate-y-1 translate-x-1 shadow-none' : 'bg-black text-white hover:bg-gray-800 hover:-translate-y-1 hover:-translate-x-1 hover:shadow-[6px_6px_0px_0px_#000]'"
        @click="copyPrompt"
      >
        {{ copied ? '✅ Скопійовано!' : 'Скопіювати промпт' }}
      </button>
    </div>
  </div>
</template>

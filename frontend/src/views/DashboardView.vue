<script setup>
import { ref, onMounted } from 'vue'
import { progressApi } from '../api/client'

const stats = ref([])
const loading = ref(true)
const exportLoading = ref(false)
const importFile = ref(null)
const importError = ref('')

onMounted(async () => {
  try {
    const { data } = await progressApi.stats()
    stats.value = data
  } finally {
    loading.value = false
  }
})

function pct(cat) {
  if (!cat.total_topics) return 0
  return Math.round((cat.studied_count / cat.total_topics) * 100)
}

async function doExport() {
  exportLoading.value = true
  try {
    const { data } = await progressApi.export()
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `studyit-progress-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(a.href)
  } finally {
    exportLoading.value = false
  }
}

function onFileChange(e) {
  importFile.value = e.target.files?.[0] ?? null
  importError.value = ''
}

async function doImport() {
  if (!importFile.value) {
    importError.value = 'Оберіть файл'
    return
  }
  importError.value = ''
  try {
    const text = await importFile.value.text()
    const data = JSON.parse(text)
    await progressApi.import(data)
    const { data: newStats } = await progressApi.stats()
    stats.value = newStats
    importFile.value = null
  } catch (e) {
    importError.value = e.response?.data?.message || e.message || 'Помилка імпорту'
  }
}
</script>

<template>
  <div>
    <h1 class="mb-8 text-4xl font-display font-black uppercase tracking-tight">Дашборд</h1>
    <div v-if="loading" class="text-slate-500 font-display font-bold text-lg">Завантаження…</div>
    <div v-else class="space-y-8">
      <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="cat in stats"
          :key="cat.slug"
          class="rounded-2xl border-[3px] border-black bg-white p-5 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:-translate-y-[2px] hover:-translate-x-[2px] hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] transition-all"
        >
          <h2 class="font-display font-bold text-xl uppercase">{{ cat.name }}</h2>
          <p class="mt-2 text-sm font-medium text-slate-700">
            <span class="font-black text-lg">{{ cat.studied_count }}</span> / {{ cat.total_topics }} вивчено
            <span v-if="cat.review_count" class="text-orange-600 font-bold"> · {{ cat.review_count }} на повторення</span>
          </p>
          <div class="mt-4 h-4 overflow-hidden rounded-full border-2 border-black bg-slate-100">
            <div
              class="h-full bg-[#4ade80] border-r-2 border-black transition-all"
              :style="{ width: pct(cat) + '%' }"
            />
          </div>
        </div>
      </div>
      <div class="panel-secondary rounded-2xl border-[3px] border-black bg-[#c7d2fe] p-6 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] mt-8">
        <h2 class="font-display font-bold text-2xl uppercase border-b-2 border-black pb-2 mb-4">Експорт / імпорт</h2>
        <div class="flex flex-col sm:flex-row flex-wrap items-start sm:items-center gap-4">
          <button
            :disabled="exportLoading"
            class="w-full sm:w-auto rounded-xl border-[3px] border-black bg-black px-6 py-3 font-display font-bold text-white transition-all shadow-[4px_4px_0px_0px_#cbd5e1] hover:-translate-y-[2px] hover:-translate-x-[2px] active:translate-y-0 active:translate-x-0 active:shadow-[0px_0px_0px_0px_#cbd5e1] disabled:opacity-50 disabled:transform-none disabled:shadow-[4px_4px_0px_0px_#cbd5e1]"
            @click="doExport"
          >
            {{ exportLoading ? 'Завантаження…' : 'Експортувати прогрес' }}
          </button>
          <div class="flex flex-col sm:flex-row flex-wrap items-stretch sm:items-center gap-3 w-full sm:w-auto">
            <input type="file" accept=".json" @change="onFileChange" class="w-full sm:w-auto font-sans font-medium file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-[3px] file:border-black file:text-sm file:font-display file:font-bold file:bg-[#fef08a] file:text-black hover:file:bg-[#fde047] file:transition-colors file:cursor-pointer" />
            <button
              type="button"
              class="w-full sm:w-auto rounded-xl border-[3px] border-black bg-white px-6 py-3 font-display font-bold transition-all shadow-[4px_4px_0px_0px_#000] hover:bg-[#bbf7d0] hover:-translate-y-[2px] hover:-translate-x-[2px] active:translate-y-0 active:translate-x-0 active:shadow-[0px_0px_0px_0px_#000]"
              @click="doImport"
            >
              Імпортувати
            </button>
          </div>
        </div>
        <p v-if="importError" class="mt-4 inline-block bg-red-100 border-2 border-black px-3 py-1 font-bold text-red-600 shadow-[2px_2px_0px_0px_#000]">{{ importError }}</p>
      </div>
    </div>
  </div>
</template>

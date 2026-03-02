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
    <h1 class="mb-6 text-2xl font-semibold">Дашборд</h1>
    <div v-if="loading" class="text-slate-500">Завантаження…</div>
    <div v-else class="space-y-6">
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="cat in stats"
          :key="cat.slug"
          class="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
        >
          <h2 class="font-medium">{{ cat.name }}</h2>
          <p class="mt-1 text-sm text-slate-600">
            {{ cat.studied_count }} / {{ cat.total_topics }} вивчено
            <span v-if="cat.review_count"> · {{ cat.review_count }} на повторення</span>
          </p>
          <div class="mt-2 h-2 overflow-hidden rounded-full bg-slate-200">
            <div
              class="h-full rounded-full bg-slate-700 transition-all"
              :style="{ width: pct(cat) + '%' }"
            />
          </div>
        </div>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <h2 class="font-medium">Експорт / імпорт</h2>
        <div class="mt-3 flex flex-wrap items-center gap-4">
          <button
            :disabled="exportLoading"
            class="rounded bg-slate-800 px-4 py-2 text-white hover:bg-slate-700 disabled:opacity-50"
            @click="doExport"
          >
            {{ exportLoading ? 'Завантаження…' : 'Експортувати прогрес' }}
          </button>
          <div class="flex items-center gap-2">
            <input type="file" accept=".json" @change="onFileChange" />
            <button
              type="button"
              class="rounded border border-slate-300 bg-white px-4 py-2 hover:bg-slate-50"
              @click="doImport"
            >
              Імпортувати
            </button>
          </div>
        </div>
        <p v-if="importError" class="mt-2 text-sm text-red-600">{{ importError }}</p>
      </div>
    </div>
  </div>
</template>

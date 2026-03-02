<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { topicsApi } from '../api/client'

const route = useRoute()
const categories = ref([])
const topics = ref([])
const loading = ref(true)
const search = ref('')
const statusFilter = ref('')

const categorySlug = ref(route.query.category || '')

async function loadCategories() {
  const { data } = await topicsApi.getCategories()
  categories.value = data
}

async function loadTopics() {
  loading.value = true
  try {
    const { data } = await topicsApi.getTopics({
      category: categorySlug.value || undefined,
      status: statusFilter.value || undefined,
      search: search.value || undefined,
    })
    topics.value = data
  } finally {
    loading.value = false
  }
}

watch([categorySlug, statusFilter, search], loadTopics)
watch(() => route.query.category, (v) => { categorySlug.value = v || '' })

onMounted(() => {
  loadCategories().then(loadTopics)
})
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-semibold">Теми</h1>
    <div class="flex gap-6">
    <aside class="w-56 shrink-0 space-y-2">
      <h2 class="font-semibold">Категорії</h2>
      <router-link
        v-for="cat in categories"
        :key="cat.slug"
        :to="{ name: 'Topics', query: { category: cat.slug } }"
        class="block rounded px-2 py-1 text-sm"
        :class="categorySlug === cat.slug ? 'bg-slate-200 font-medium' : 'hover:bg-slate-100'"
      >
        {{ cat.name }}
        <span class="text-slate-500">({{ cat.total_topics }})</span>
      </router-link>
    </aside>
    <div class="min-w-0 flex-1">
      <div class="mb-4 flex flex-wrap items-center gap-4">
        <input
          v-model="search"
          type="search"
          placeholder="Пошук тем..."
          class="rounded border border-slate-300 px-3 py-2"
        />
        <select v-model="statusFilter" class="rounded border border-slate-300 px-3 py-2">
          <option value="">Усі</option>
          <option value="new">Нові</option>
          <option value="studied">Вивчені</option>
          <option value="review">На повторення</option>
        </select>
      </div>
      <div v-if="loading" class="text-slate-500">Завантаження…</div>
      <div v-else class="space-y-2">
        <router-link
          v-for="t in topics"
          :key="t.id"
          :to="{ name: 'TopicDetail', params: { id: t.id } }"
          class="flex items-center justify-between rounded-lg border border-slate-200 bg-white p-3 shadow-sm hover:bg-slate-50"
        >
          <span class="font-medium">{{ t.title }}</span>
          <span
            class="rounded px-2 py-0.5 text-xs"
            :class="{
              'bg-slate-200': t.status === 'new',
              'bg-green-100 text-green-800': t.status === 'studied',
              'bg-amber-100 text-amber-800': t.status === 'review',
            }"
          >
            {{ t.status === 'new' ? 'Нова' : t.status === 'studied' ? 'Вивчено' : 'Повторити' }}
          </span>
        </router-link>
      </div>
    </div>
    </div>
  </div>
</template>
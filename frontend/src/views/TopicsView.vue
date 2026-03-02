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
  <div class="space-y-8">
    <h1 class="text-4xl font-display font-black uppercase tracking-tight">Теми</h1>
    <div class="flex flex-col md:flex-row gap-8">
    <aside class="w-full md:w-64 shrink-0 space-y-3">
      <h2 class="font-display font-bold text-xl uppercase border-b-2 border-black pb-2 mb-4">Категорії</h2>
      <router-link
        v-for="cat in categories"
        :key="cat.slug"
        :to="{ name: 'Topics', query: { category: cat.slug } }"
        class="block rounded-xl border-[3px] border-transparent px-3 py-2 text-base font-medium transition-all"
        :class="categorySlug === cat.slug ? 'bg-[#fef08a] border-black shadow-[4px_4px_0px_0px_#000] -translate-y-0.5' : 'hover:bg-white hover:border-black hover:shadow-[4px_4px_0px_0px_#000] hover:-translate-y-0.5'"
      >
        {{ cat.name }}
        <span class="font-display font-bold ml-1">({{ cat.total_topics }})</span>
      </router-link>
    </aside>
    <div class="min-w-0 flex-1">
      <div class="mb-6 flex flex-col sm:flex-row flex-wrap items-stretch sm:items-center gap-4">
        <input
          v-model="search"
          type="search"
          placeholder="Пошук тем..."
          class="rounded-xl border-[3px] border-black px-4 py-3 font-sans font-medium focus:outline-none focus:bg-[#fef08a] transition-colors shadow-[4px_4px_0px_0px_#000] flex-1 min-w-[200px]"
        />
        <select v-model="statusFilter" class="rounded-xl border-[3px] border-black px-4 py-3 font-display font-bold focus:outline-none focus:bg-[#fef08a] transition-colors shadow-[4px_4px_0px_0px_#000] w-full sm:w-auto">
          <option value="">Усі статуси</option>
          <option value="new">Нові</option>
          <option value="studied">Вивчені</option>
          <option value="review">На повторення</option>
        </select>
      </div>
      <div v-if="loading" class="text-slate-500 font-display font-bold text-lg">Завантаження…</div>
      <div v-else class="space-y-4">
        <router-link
          v-for="t in topics"
          :key="t.id"
          :to="{ name: 'TopicDetail', params: { id: t.id } }"
          class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-4 rounded-xl border-[3px] border-black bg-white p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:-translate-y-1 hover:-translate-x-1 hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] transition-all active:translate-y-0 active:translate-x-0 active:shadow-[0px_0px_0px_0px_rgba(0,0,0,1)]"
        >
          <span class="font-bold text-lg">{{ t.title }}</span>
          <span
            class="inline-block shrink-0 rounded-lg border-2 border-black px-3 py-1 font-display font-bold text-sm shadow-[2px_2px_0px_0px_#000]"
            :class="{
              'bg-[#a5f3fc]': t.status === 'new',
              'bg-[#4ade80]': t.status === 'studied',
              'bg-[#f97316] text-white': t.status === 'review',
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
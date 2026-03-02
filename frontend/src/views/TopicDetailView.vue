<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { topicsApi } from '../api/client'
import MarkdownContent from '../components/MarkdownContent.vue'

const route = useRoute()
const topic = ref(null)
const notes = ref([])
const loading = ref(true)
const newNoteText = ref('')
const editingNoteId = ref(null)
const editingNoteText = ref('')

async function load() {
  loading.value = true
  try {
    const { data } = await topicsApi.getTopic(route.params.id)
    topic.value = data
    const { data: notesData } = await topicsApi.getNotes(data.id)
    notes.value = notesData
  } finally {
    loading.value = false
  }
}

async function setStatus(status) {
  await topicsApi.updateStatus(topic.value.id, status)
  topic.value.status = status
}

async function addNote() {
  if (!newNoteText.value.trim()) return
  await topicsApi.createNote(topic.value.id, newNoteText.value.trim())
  const { data } = await topicsApi.getNotes(topic.value.id)
  notes.value = data
  newNoteText.value = ''
}

function startEdit(note) {
  editingNoteId.value = note.id
  editingNoteText.value = note.text
}

async function saveNote() {
  if (editingNoteId.value == null) return
  await topicsApi.updateNote(editingNoteId.value, editingNoteText.value)
  const { data } = await topicsApi.getNotes(topic.value.id)
  notes.value = data
  editingNoteId.value = null
}

async function deleteNote(noteId) {
  await topicsApi.deleteNote(noteId)
  notes.value = notes.value.filter((n) => n.id !== noteId)
}

onMounted(load)
watch(() => route.params.id, load)
</script>

<template>
  <div v-if="loading" class="text-slate-500">Завантаження…</div>
  <div v-else-if="topic" class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-4">
      <h1 class="text-2xl font-semibold">{{ topic.title }}</h1>
      <div class="flex gap-2">
        <button
          type="button"
          class="rounded px-3 py-1 text-sm"
          :class="topic.status === 'studied' ? 'bg-slate-700 text-white' : 'bg-slate-200 hover:bg-slate-300'"
          @click="setStatus('studied')"
        >
          Вивчив
        </button>
        <button
          type="button"
          class="rounded px-3 py-1 text-sm"
          :class="topic.status === 'review' ? 'bg-amber-600 text-white' : 'bg-slate-200 hover:bg-slate-300'"
          @click="setStatus('review')"
        >
          На повторення
        </button>
        <button
          type="button"
          class="rounded px-3 py-1 text-sm bg-slate-200 hover:bg-slate-300"
          @click="setStatus('new')"
        >
          Нова
        </button>
      </div>
    </div>
    <div class="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h2 class="mb-2 text-lg font-medium">Коротка відповідь</h2>
      <MarkdownContent :content="topic.short_answer" />
    </div>
    <div class="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h2 class="mb-2 text-lg font-medium">Детальне пояснення</h2>
      <MarkdownContent :content="topic.detailed_explanation" />
    </div>
    <div class="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h2 class="mb-3 text-lg font-medium">Замітки</h2>
      <div class="space-y-2">
        <div v-for="note in notes" :key="note.id" class="flex items-start justify-between gap-2 rounded bg-slate-50 p-2">
          <template v-if="editingNoteId === note.id">
            <input v-model="editingNoteText" class="min-w-0 flex-1 rounded border px-2 py-1" />
            <button type="button" class="rounded bg-slate-700 px-2 py-1 text-white text-sm" @click="saveNote">Зберегти</button>
          </template>
          <template v-else>
            <p class="min-w-0 flex-1 text-sm">{{ note.text }}</p>
            <div class="flex gap-1">
              <button type="button" class="text-slate-600 hover:text-slate-800" @click="startEdit(note)">Редагувати</button>
              <button type="button" class="text-red-600 hover:text-red-800" @click="deleteNote(note.id)">Видалити</button>
            </div>
          </template>
        </div>
      </div>
      <div class="mt-3 flex gap-2">
        <input v-model="newNoteText" placeholder="Нова замітка..." class="min-w-0 flex-1 rounded border border-slate-300 px-3 py-2" @keydown.enter.prevent="addNote" />
        <button type="button" class="rounded bg-slate-800 px-4 py-2 text-white hover:bg-slate-700" @click="addNote">Додати</button>
      </div>
    </div>
  </div>
</template>

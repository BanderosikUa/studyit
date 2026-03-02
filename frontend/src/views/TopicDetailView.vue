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
  <div v-if="loading" class="text-slate-500 font-display font-bold">Завантаження…</div>
  <div v-else-if="topic" class="space-y-8">
    <div class="flex flex-col md:flex-row flex-wrap items-center justify-center md:justify-between gap-6 bg-[#fcd34d] p-6 rounded-2xl border-[3px] border-black shadow-[6px_6px_0px_0px_#000]">
      <h1 class="text-2xl md:text-3xl font-display font-black uppercase tracking-tight text-center md:text-left">{{ topic.title }}</h1>
      <div class="flex flex-wrap justify-center gap-2 md:gap-3 w-full md:w-auto">
        <button
          type="button"
          class="rounded-xl border-[3px] border-black px-4 py-2 font-display font-bold text-sm transition-all shadow-[4px_4px_0px_0px_#000] hover:-translate-y-[2px] hover:-translate-x-[2px] active:translate-y-0 active:translate-x-0 active:shadow-[0px_0px_0px_0px_#000]"
          :class="topic.status === 'studied' ? 'bg-[#4ade80]' : 'bg-white hover:bg-[#bbf7d0]'"
          @click="setStatus('studied')"
        >
          Вивчив
        </button>
        <button
          type="button"
          class="rounded-xl border-[3px] border-black px-4 py-2 font-display font-bold text-sm transition-all shadow-[4px_4px_0px_0px_#000] hover:-translate-y-[2px] hover:-translate-x-[2px] active:translate-y-0 active:translate-x-0 active:shadow-[0px_0px_0px_0px_#000]"
          :class="topic.status === 'review' ? 'bg-[#f97316] text-white' : 'bg-white hover:bg-[#fed7aa]'"
          @click="setStatus('review')"
        >
          На повторення
        </button>
        <button
          type="button"
          class="rounded-xl border-[3px] border-black px-4 py-2 font-display font-bold text-sm transition-all shadow-[4px_4px_0px_0px_#000] bg-white hover:bg-[#a5f3fc] hover:-translate-y-[2px] hover:-translate-x-[2px] active:translate-y-0 active:translate-x-0 active:shadow-[0px_0px_0px_0px_#000]"
          :class="topic.status === 'new' ? 'bg-[#22d3ee]' : ''"
          @click="setStatus('new')"
        >
          Нова
        </button>
      </div>
    </div>

    <div class="rounded-2xl border-[3px] border-black bg-white p-6 md:p-8 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">
      <h2 class="mb-4 text-xl font-display font-bold uppercase tracking-tight border-b-2 border-black pb-2">Коротка відповідь</h2>
      <MarkdownContent :content="topic.short_answer" />
    </div>

    <div class="rounded-2xl border-[3px] border-black bg-white p-6 md:p-8 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">
      <h2 class="mb-4 text-xl font-display font-bold uppercase tracking-tight border-b-2 border-black pb-2">Детальне пояснення</h2>
      <MarkdownContent :content="topic.detailed_explanation" />
    </div>

    <div class="rounded-2xl border-[3px] border-black bg-[#e0e7ff] p-6 md:p-8 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">
      <h2 class="mb-6 text-xl font-display font-bold uppercase tracking-tight border-b-2 border-black pb-2">Замітки</h2>
      <div class="space-y-4">
        <div v-for="note in notes" :key="note.id" class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 rounded-xl border-[3px] border-black bg-white p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <template v-if="editingNoteId === note.id">
            <input v-model="editingNoteText" class="min-w-0 w-full sm:flex-1 rounded-lg border-2 border-black px-3 py-2 font-sans focus:outline-none focus:ring-2 focus:ring-black" />
            <button type="button" class="w-full sm:w-auto rounded-lg border-2 border-black bg-[#4ade80] px-4 py-2 font-display font-bold text-sm transition-all shadow-[2px_2px_0px_0px_#000] active:translate-y-[2px] active:shadow-none" @click="saveNote">Зберегти</button>
          </template>
          <template v-else>
            <p class="min-w-0 w-full sm:flex-1 text-base font-medium">{{ note.text }}</p>
            <div class="flex flex-wrap gap-2 w-full sm:w-auto">
              <button type="button" class="rounded-lg border-2 border-black bg-[#fef08a] px-3 py-1 font-display font-bold text-xs transition-all shadow-[2px_2px_0px_0px_#000] active:translate-y-[2px] active:translate-x-[2px] active:shadow-none" @click="startEdit(note)">Редаг.</button>
              <button type="button" class="rounded-lg border-2 border-black bg-[#fca5a5] px-3 py-1 font-display font-bold text-xs transition-all shadow-[2px_2px_0px_0px_#000] active:translate-y-[2px] active:translate-x-[2px] active:shadow-none" @click="deleteNote(note.id)">Видал.</button>
            </div>
          </template>
        </div>
      </div>
      <div class="mt-6 flex flex-col sm:flex-row flex-wrap gap-3">
        <input v-model="newNoteText" placeholder="Нова замітка..." class="min-w-0 w-full sm:flex-1 rounded-xl border-[3px] border-black px-4 py-3 font-sans font-medium focus:outline-none focus:bg-[#fef08a] transition-colors" @keydown.enter.prevent="addNote" />
        <button type="button" class="w-full sm:w-auto rounded-xl border-[3px] border-black bg-black px-6 py-3 font-display font-bold text-white transition-all shadow-[4px_4px_0px_0px_#cbd5e1] hover:-translate-y-[2px] hover:-translate-x-[2px] active:translate-y-0 active:translate-x-0 active:shadow-[0px_0px_0px_0px_#cbd5e1]" @click="addNote">Додати</button>
      </div>
    </div>
  </div>
</template>

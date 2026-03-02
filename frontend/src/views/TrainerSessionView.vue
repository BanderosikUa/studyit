<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { trainerApi } from '../api/client'

const route = useRoute()
const router = useRouter()
const session = ref(null)
const currentIndex = ref(0)
const userAnswer = ref('')
const submitting = ref(false)

const currentQuestion = computed(() => {
  if (!session.value?.questions?.length) return null
  return session.value.questions[currentIndex.value]
})

const progressPct = computed(() => {
  if (!session.value?.questions?.length) return 0
  return Math.round(((currentIndex.value + 1) / session.value.questions.length) * 100)
})

const isLast = computed(() => {
  if (!session.value?.questions?.length) return true
  return currentIndex.value >= session.value.questions.length - 1
})

onMounted(async () => {
  const { data } = await trainerApi.getSession(route.params.id)
  session.value = data
  if (data.questions?.length) {
    const q = data.questions[0]
    userAnswer.value = q.user_answer || ''
  }
})

async function next() {
  if (!currentQuestion.value) return
  submitting.value = true
  try {
    await trainerApi.submitAnswer(
      Number(route.params.id),
      currentQuestion.value.topic_id,
      userAnswer.value
    )
    if (isLast.value) {
      router.push({ name: 'TrainerResults', params: { id: route.params.id } })
    } else {
      currentIndex.value++
      const nextQ = session.value.questions[currentIndex.value]
      userAnswer.value = nextQ?.user_answer || ''
    }
  } finally {
    submitting.value = false
  }
}

function skip() {
  if (isLast.value) {
    router.push({ name: 'TrainerResults', params: { id: route.params.id } })
  } else {
    currentIndex.value++
    const nextQ = session.value.questions[currentIndex.value]
    userAnswer.value = nextQ?.user_answer || ''
  }
}
</script>

<template>
  <div v-if="!session" class="text-slate-500">Завантаження…</div>
  <div v-else class="mx-auto max-w-2xl space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold">Тренажер</h1>
      <span class="text-slate-600">{{ currentIndex + 1 }} / {{ session.questions?.length || 0 }}</span>
    </div>
    <div class="h-2 overflow-hidden rounded-full bg-slate-200">
      <div class="h-full rounded-full bg-slate-700 transition-all" :style="{ width: progressPct + '%' }" />
    </div>
    <div v-if="currentQuestion" class="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h2 class="mb-4 text-lg font-medium">{{ currentQuestion.title }}</h2>
      <textarea
        v-model="userAnswer"
        rows="8"
        placeholder="Ваша відповідь..."
        class="w-full rounded border border-slate-300 px-3 py-2"
      />
      <div class="mt-4 flex justify-between">
        <button type="button" class="rounded border border-slate-300 px-4 py-2 hover:bg-slate-50" @click="skip">
          Пропустити
        </button>
        <button
          type="button"
          :disabled="submitting"
          class="rounded bg-slate-800 px-4 py-2 text-white hover:bg-slate-700 disabled:opacity-50"
          @click="next"
        >
          {{ isLast ? 'Завершити' : 'Далі' }}
        </button>
      </div>
    </div>
  </div>
</template>

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
  <div v-if="!session" class="text-slate-500 font-display font-bold text-lg text-center mt-12">Завантаження…</div>
  <div v-else class="mx-auto max-w-2xl space-y-8 mt-4">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-display font-black uppercase tracking-tight">Тренажер</h1>
      <span class="font-display font-bold text-xl text-black px-3 py-1 bg-[#fcd34d] border-2 border-black rounded-lg shadow-[2px_2px_0px_0px_#000]">{{ currentIndex + 1 }} / {{ session.questions?.length || 0 }}</span>
    </div>
    <div class="h-4 overflow-hidden rounded-full border-[3px] border-black bg-slate-100">
      <div class="h-full bg-[#a5f3fc] border-r-[3px] border-black transition-all duration-300 ease-out" :style="{ width: progressPct + '%' }" />
    </div>
    <div v-if="currentQuestion" class="rounded-2xl border-[3px] border-black bg-white p-6 md:p-8 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">
      <h2 class="mb-6 text-2xl font-display font-bold">{{ currentQuestion.title }}</h2>
      <textarea
        v-model="userAnswer"
        rows="8"
        placeholder="Ваша відповідь..."
        class="w-full rounded-xl border-[3px] border-black px-4 py-4 font-sans font-medium text-lg focus:outline-none focus:bg-[#fef08a] transition-colors shadow-[inset_0px_4px_0px_0px_rgba(0,0,0,0.05)] resize-y"
      />
      <div class="mt-6 flex flex-col sm:flex-row flex-wrap justify-between gap-4">
        <button type="button" class="w-full sm:w-auto rounded-xl border-[3px] border-black bg-white px-6 py-3 font-display font-bold transition-all shadow-[4px_4px_0px_0px_#000] hover:bg-slate-100 hover:-translate-y-1 hover:-translate-x-1 hover:shadow-[6px_6px_0px_0px_#000] active:translate-y-0 active:translate-x-0 active:shadow-[0px_0px_0px_0px_#000] text-lg uppercase" @click="skip">
          Пропустити
        </button>
        <button
          type="button"
          :disabled="submitting"
          class="w-full sm:w-auto rounded-xl border-[3px] border-black bg-black px-8 py-3 font-display font-black text-white transition-all shadow-[4px_4px_0px_0px_#cbd5e1] hover:-translate-y-1 hover:-translate-x-1 hover:shadow-[6px_6px_0px_0px_#cbd5e1] active:translate-y-0 active:translate-x-0 active:shadow-[0px_0px_0px_0px_#cbd5e1] disabled:opacity-50 disabled:transform-none disabled:shadow-[4px_4px_0px_0px_#cbd5e1] text-lg uppercase tracking-wide"
          @click="next"
        >
          {{ isLast ? 'Завершити' : 'Далі' }}
        </button>
      </div>
    </div>
  </div>
</template>

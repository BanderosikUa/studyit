import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (r) => r,
  async (err) => {
    const orig = err.config
    if (err.response?.status === 401 && !orig._retry) {
      orig._retry = true
      const refresh = localStorage.getItem('refresh')
      if (refresh) {
        try {
          const { data } = await axios.post('/api/auth/refresh/', { refresh })
          localStorage.setItem('access', data.access)
          orig.headers.Authorization = `Bearer ${data.access}`
          return api(orig)
        } catch (_) {
          localStorage.removeItem('access')
          localStorage.removeItem('refresh')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(err)
  }
)

export default api

export const authApi = {
  register: (email, password) => api.post('/auth/register/', { email, password }),
  login: (email, password) => api.post('/auth/login/', { email, password }),
}

export const topicsApi = {
  getCategories: () => api.get('/topics/categories/'),
  getTopics: (params) => api.get('/topics/', { params }),
  getTopic: (id) => api.get(`/topics/${id}/`),
  updateStatus: (id, status) => api.post(`/topics/${id}/status/`, { status }),
  getNotes: (topicId) => api.get(`/topics/${topicId}/notes/`),
  createNote: (topicId, text) => api.post(`/topics/${topicId}/notes/`, { text }),
  updateNote: (noteId, text) => api.put(`/topics/notes/${noteId}/`, { text }),
  deleteNote: (noteId) => api.delete(`/topics/notes/${noteId}/delete/`),
}

export const trainerApi = {
  createSession: (category, total_questions) =>
    api.post('/trainer/sessions/', { category: category || null, total_questions }),
  getSession: (id) => api.get(`/trainer/sessions/${id}/`),
  submitAnswer: (sessionId, topicId, user_answer, self_score) =>
    api.post(`/trainer/sessions/${sessionId}/answer/`, {
      topic_id: topicId,
      user_answer,
      self_score: self_score ?? null,
    }),
  getPrompt: (sessionId) => api.get(`/trainer/sessions/${sessionId}/prompt/`),
}

export const progressApi = {
  export: () => api.get('/progress/export/'),
  import: (data) => api.post('/progress/import/', data),
  stats: () => api.get('/progress/stats/'),
}

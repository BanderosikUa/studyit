<script setup>
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.min.css'

const props = defineProps({
  content: { type: String, default: '' },
})

const md = new MarkdownIt({
  highlight(str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (_) {}
    }
    return ''
  },
})

const html = computed(() => md.render(props.content || ''))
</script>

<template>
  <div class="markdown-body max-w-none" v-html="html" />
</template>

<style scoped>
.markdown-body :deep(pre) {
  overflow-x: auto;
  background: #f1f5f9;
  padding: 1rem;
  border-radius: 0.5rem;
}
.markdown-body :deep(code) {
  background: #f1f5f9;
  padding: 0.125rem 0.25rem;
  font-family: ui-monospace, monospace;
  font-size: 0.875rem;
  border-radius: 0.25rem;
}
.markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
}
.markdown-body :deep(h1) { font-size: 1.25rem; font-weight: 700; }
.markdown-body :deep(h2) { margin-top: 1rem; font-size: 1.125rem; font-weight: 600; }
.markdown-body :deep(h3) { margin-top: 0.75rem; font-weight: 500; }
.markdown-body :deep(ul) { list-style-type: disc; padding-left: 1.5rem; }
.markdown-body :deep(p) { margin: 0.5rem 0; }
</style>

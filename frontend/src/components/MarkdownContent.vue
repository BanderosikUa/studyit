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
  background: #ffffff;
  padding: 1.25rem;
  border: 3px solid #000;
  border-radius: 0.75rem;
  box-shadow: 4px 4px 0px 0px #000;
  margin: 1.5rem 0;
}
.markdown-body :deep(code) {
  background: #fef08a;
  padding: 0.125rem 0.375rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 0.875rem;
  border: 2px solid #000;
  border-radius: 0.375rem;
  font-weight: 700;
  color: #000;
}
.markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
  border: none;
  font-weight: 500;
  color: inherit;
}
.markdown-body :deep(h1) {
  font-family: var(--font-display, 'Space Grotesk', sans-serif);
  font-size: 2rem;
  font-weight: 900;
  text-transform: uppercase;
  margin-top: 2rem;
  margin-bottom: 1rem;
  border-bottom: 3px solid #000;
  padding-bottom: 0.5rem;
}
.markdown-body :deep(h2) {
  font-family: var(--font-display, 'Space Grotesk', sans-serif);
  font-size: 1.5rem;
  font-weight: 900;
  text-transform: uppercase;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}
.markdown-body :deep(h3) {
  font-family: var(--font-display, 'Space Grotesk', sans-serif);
  font-size: 1.25rem;
  font-weight: 800;
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
}
.markdown-body :deep(ul) {
  list-style-type: square;
  padding-left: 1.5rem;
  margin-bottom: 1rem;
  font-weight: 500;
}
.markdown-body :deep(ol) {
  list-style-type: decimal;
  padding-left: 1.5rem;
  margin-bottom: 1rem;
  font-weight: 600;
}
.markdown-body :deep(li) {
  margin-bottom: 0.5rem;
}
.markdown-body :deep(p) {
  margin: 1rem 0;
  font-size: 1.05rem;
  line-height: 1.6;
}
.markdown-body :deep(blockquote) {
  margin: 1.5rem 0;
  font-style: italic;
  background: #e0e7ff;
  padding: 1.25rem;
  border: 3px solid #000;
  border-radius: 0.75rem;
  box-shadow: 4px 4px 0px 0px #000;
  font-weight: 600;
}
.markdown-body :deep(a) {
  font-weight: 800;
  text-decoration: underline;
  text-decoration-thickness: 2px;
  transition: all 0.2s ease;
}
.markdown-body :deep(a:hover) {
  background: #fef08a;
  color: #000;
}
</style>

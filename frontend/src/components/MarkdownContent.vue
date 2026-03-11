<script setup>
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.min.css'

const props = defineProps({
  content: { type: String, default: '' },
})

function normalizeBrokenLists(markdown) {
  const lines = (markdown || '').replaceAll('\r\n', '\n').split('\n')

  for (let index = 0; index < lines.length; index += 1) {
    const currentLine = lines[index]
    const markerMatch = currentLine.match(/^(\s*)([-*+])\s*$/)
    if (!markerMatch) continue

    let nextLineIndex = index + 1
    while (nextLineIndex < lines.length && lines[nextLineIndex].trim() === '') {
      nextLineIndex += 1
    }
    if (nextLineIndex >= lines.length) continue

    const nextLine = lines[nextLineIndex].trim()
    if (!nextLine) continue

    if (
      /^(```|~~~|>|#{1,6}\s)/.test(nextLine) ||
      /^([-*+]\s+|\d+\.\s+)/.test(nextLine) ||
      /^(\|.+\||---+$|\*\*\*+$|___+$)/.test(nextLine)
    ) {
      continue
    }

    lines[index] = `${markerMatch[1]}${markerMatch[2]} ${nextLine}`
    lines.splice(index + 1, nextLineIndex - index)
  }

  return lines.join('\n')
}

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

const html = computed(() => md.render(normalizeBrokenLists(props.content)))
</script>

<template>
  <div class="markdown-body max-w-none" v-html="html" />
</template>

<style scoped>
.markdown-body {
  color: inherit;
}

.markdown-body :deep(pre) {
  overflow-x: auto;
  background: var(--markdown-pre-bg, #ffffff);
  padding: 1.25rem;
  border: 3px solid var(--markdown-border, #000);
  border-radius: 0.75rem;
  box-shadow: 4px 4px 0px 0px var(--markdown-shadow, #000);
  margin: 1.5rem 0;
}
.markdown-body :deep(code) {
  background: var(--markdown-inline-code-bg, #fef08a);
  padding: 0.125rem 0.375rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 0.875rem;
  border: 2px solid var(--markdown-border, #000);
  border-radius: 0.375rem;
  font-weight: 700;
  color: var(--markdown-inline-code-text, #000);
}
.markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
  border: none;
  font-weight: 500;
  color: inherit;
}
.markdown-body :deep(pre code.hljs) {
  background: transparent;
  color: var(--markdown-code-text, inherit);
}
.markdown-body :deep(h1) {
  font-family: var(--font-display, 'Space Grotesk', sans-serif);
  font-size: 2rem;
  font-weight: 900;
  text-transform: uppercase;
  margin-top: 2rem;
  margin-bottom: 1rem;
  border-bottom: 3px solid var(--markdown-border, #000);
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
  list-style-type: disc;
  list-style-position: outside;
  padding-left: 1.75rem;
  margin: 1rem 0;
  font-weight: 500;
}
.markdown-body :deep(ol) {
  list-style-type: decimal;
  list-style-position: outside;
  padding-left: 1.75rem;
  margin: 1rem 0;
  font-weight: 600;
}
.markdown-body :deep(li) {
  margin: 0.45rem 0;
}
.markdown-body :deep(li > p) {
  margin: 0;
}
.markdown-body :deep(li > p + p) {
  margin-top: 0.5rem;
}
.markdown-body :deep(li > ul),
.markdown-body :deep(li > ol) {
  margin-top: 0.5rem;
}
.markdown-body :deep(p) {
  margin: 1rem 0;
  font-size: 1.05rem;
  line-height: 1.6;
}
.markdown-body :deep(blockquote) {
  margin: 1.5rem 0;
  font-style: italic;
  background: var(--markdown-blockquote-bg, #e0e7ff);
  padding: 1.25rem;
  border: 3px solid var(--markdown-border, #000);
  border-radius: 0.75rem;
  box-shadow: 4px 4px 0px 0px var(--markdown-shadow, #000);
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
